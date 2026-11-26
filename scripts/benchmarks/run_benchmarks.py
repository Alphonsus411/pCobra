"""Benchmark script.

La política de targets se hereda de ``src/pcobra/cobra/transpilers/targets.py``
a través de ``scripts/benchmarks/targets_policy.py``.
"""

import argparse
import json
import math
import os
import shutil
import signal
import subprocess
import sys
import tempfile
import textwrap
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "src"))

from scripts.benchmarks.targets_policy import (
    BENCHMARK_BACKEND_METADATA,
    executable_benchmark_backends,
    validate_backend_metadata,
    validate_local_targets_policy,
)

# Código Cobra para las pruebas de rendimiento
CODE = """
var x = 0
mientras x <= 1000 :
    x = x + 1
fin
imprimir(x)
"""

# Metadata técnica común por backend (extensiones/comandos)
BACKEND_METADATA = BENCHMARK_BACKEND_METADATA


def run_and_measure(
    cmd: list[str], env: dict[str, str] | None = None
) -> tuple[float, int]:
    """Mide tiempo y RSS individual en Linux y valida la salida funcional."""
    linux_time = Path("/usr/bin/time")
    if sys.platform != "linux" or not linux_time.is_file():
        raise RuntimeError("Benchmarks requieren Linux con GNU time")
    with tempfile.TemporaryDirectory() as tmpdir:
        metrics = Path(tmpdir) / "rss"
        measured_cmd = [
            str(linux_time),
            "-q",
            "-f",
            "%M",
            "-o",
            str(metrics),
            "--",
            *cmd,
        ]
        start = time.perf_counter()
        with subprocess.Popen(
            measured_cmd,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            start_new_session=True,
        ) as proc:
            try:
                stdout, stderr = proc.communicate(timeout=120)
            except subprocess.TimeoutExpired:
                try:
                    os.killpg(proc.pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass
                proc.communicate()
                raise
            elapsed = time.perf_counter() - start
            if proc.returncode:
                raise subprocess.CalledProcessError(
                    proc.returncode, cmd, output=stdout, stderr=stderr
                )
        if stdout.strip() != "1001":
            raise RuntimeError(f"Salida funcional inesperada: {stdout!r}")
        mem_kb = int(metrics.read_text(encoding="ascii").strip())
        if not math.isfinite(elapsed) or elapsed <= 0 or mem_kb <= 0:
            raise RuntimeError("Medición de tiempo o memoria inválida")
    return elapsed, mem_kb


def main() -> None:
    parser = argparse.ArgumentParser(description="Ejecuta benchmarks por backend")
    parser.add_argument(
        "--include-best-effort-runtime",
        action="store_true",
        help=(
            "Incluye runtimes best-effort no públicos (go/java). "
            "Por defecto solo se ejecutan runtimes oficiales."
        ),
    )
    parser.add_argument(
        "--include-transpilation-only",
        action="store_true",
        help=(
            "Permite intentar ejecutar targets solo de transpilación (wasm/asm). "
            "Úsalo solo en modo experimental explícito."
        ),
    )
    args = parser.parse_args()

    repo_root = REPO_ROOT
    validate_backend_metadata(BACKEND_METADATA, context="run_benchmarks")
    validate_local_targets_policy(repo_root)

    env = os.environ.copy()
    env["PYTHONPATH"] = str(repo_root / "src")
    results = []
    with tempfile.TemporaryDirectory() as tmpdir:
        config = Path(tmpdir) / "cobra.toml"
        config.touch()
        env["COBRA_TOML"] = str(config)
        co_file = Path(tmpdir) / "program.cobra"
        co_file.write_text(CODE, encoding="utf-8")
        selected_backends = list(
            executable_benchmark_backends(
                BACKEND_METADATA,
                include_experimental=args.include_best_effort_runtime,
            )
        )
        if args.include_transpilation_only:
            selected_backends.extend(
                target for target in ("wasm", "asm") if target in BACKEND_METADATA
            )

        for backend in selected_backends:
            cfg = BACKEND_METADATA[backend]
            run_cmd = cfg["run"]
            src_file = Path(tmpdir) / f"program.{cfg['ext']}"
            transp_cmd = [
                sys.executable,
                "-c",
                (
                    "import sys; from pathlib import Path; "
                    "from pcobra.cobra.build import backend_pipeline; "
                    "result = backend_pipeline.build(sys.argv[1], "
                    "{'preferred_backend': sys.argv[2]}); "
                    "assert result['backend'] == sys.argv[2], 'Backend inesperado'; "
                    "Path(sys.argv[3]).write_text(result['code'], encoding='utf-8')"
                ),
                str(co_file),
                backend,
                str(src_file),
            ]
            try:
                subprocess.run(
                    transp_cmd,
                    env=env,
                    check=True,
                    capture_output=True,
                    text=True,
                    timeout=120,
                )
            except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as err:
                raise RuntimeError(
                    f"Falló la transpilación de benchmarks para {backend}"
                ) from err
            if (
                not src_file.is_file()
                or not src_file.read_text(encoding="utf-8").strip()
            ):
                raise RuntimeError(f"Código generado vacío para {backend}")
            if backend == "rust":
                body = "\n".join(
                    line
                    for line in src_file.read_text(encoding="utf-8").splitlines()
                    if line.strip()
                    not in {
                        "use crate::corelibs::*;",
                        "use crate::standard_library::*;",
                    }
                )
                src_file.write_text(
                    f"fn main() {{\n{textwrap.indent(body, '    ')}\n}}\n",
                    encoding="utf-8",
                )
            if backend == "javascript":
                native_dir = repo_root / "src" / "pcobra" / "core" / "nativos"
                if not native_dir.is_dir():
                    raise RuntimeError(f"Runtime JavaScript ausente: {native_dir}")
                shutil.copytree(native_dir, Path(tmpdir) / "nativos")
            if "compile" in cfg:
                compile_cmd = [
                    arg.format(file=src_file, tmp=tmpdir) for arg in cfg["compile"]
                ]
                try:
                    subprocess.run(compile_cmd, env=env, check=True, timeout=120)
                except (
                    subprocess.CalledProcessError,
                    subprocess.TimeoutExpired,
                ) as err:
                    raise RuntimeError(
                        f"Falló la compilación para {backend}"
                    ) from err
            cmd = [arg.format(file=src_file, tmp=tmpdir) for arg in run_cmd]
            if not shutil.which(cmd[0]) and not os.path.exists(cmd[0]):
                raise RuntimeError(f"Runtime no disponible para {backend}: {cmd[0]}")
            elapsed, mem = run_and_measure(cmd, env)
            results.append({"backend": backend, "time": elapsed, "memory_kb": mem})
    if not results or len(results) != len(selected_backends):
        raise RuntimeError("Benchmarks incompletos")
    print(json.dumps(results, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
