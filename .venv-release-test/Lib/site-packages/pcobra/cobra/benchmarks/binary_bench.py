"""Benchmark de binarios ejecutable desde el paquete instalable.

Nota de contrato: ``scripts/`` solo contiene wrappers de tooling y **no** es una
ruta de import soportada en distribución.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import tempfile
import time
import sys
from pathlib import Path

from pcobra.cobra.benchmarks.targets_policy import (
    BINARY_BENCHMARK_METADATA,
    executable_benchmark_backends,
    validate_backend_metadata,
)
from pcobra.cobra.core.cobra_config import tiempo_max_transpilacion

try:
    import resource
except ImportError:  # pragma: no cover - Windows
    resource = None  # type: ignore
    try:
        import psutil  # type: ignore
    except ImportError:  # pragma: no cover - psutil no está disponible
        psutil = None  # type: ignore
else:
    psutil = None  # type: ignore

CODE = """
var x = 0
mientras x <= 1000 :
    x = x + 1
fin
imprimir(x)
"""

SUBPROCESS_TIMEOUT = tiempo_max_transpilacion()


def run_and_measure(cmd: list[str], env: dict[str, str] | None = None) -> tuple[float, int]:
    """Ejecuta *cmd* y devuelve ``(tiempo_en_segundos, memoria_en_kb)``."""
    start_time = time.perf_counter()
    if resource is not None:
        start_usage = resource.getrusage(resource.RUSAGE_CHILDREN)
        subprocess.run(
            cmd,
            env=env,
            check=False,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.STDOUT,
            timeout=SUBPROCESS_TIMEOUT,
        )
        elapsed = time.perf_counter() - start_time
        end_usage = resource.getrusage(resource.RUSAGE_CHILDREN)
        mem_kb = max(0, end_usage.ru_maxrss - start_usage.ru_maxrss)
    elif psutil is not None:
        proc = subprocess.Popen(
            cmd,
            env=env,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.STDOUT,
        )
        ps_proc = psutil.Process(proc.pid)  # type: ignore[attr-defined]
        peak = 0
        while proc.poll() is None:
            try:
                rss = ps_proc.memory_info().rss
            except psutil.Error:  # type: ignore[attr-defined]
                break
            peak = max(peak, rss)
            time.sleep(0.01)
        proc.wait(timeout=SUBPROCESS_TIMEOUT)
        elapsed = time.perf_counter() - start_time
        mem_kb = peak // 1024
    else:
        subprocess.run(
            cmd,
            env=env,
            check=False,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.STDOUT,
            timeout=SUBPROCESS_TIMEOUT,
        )
        elapsed = time.perf_counter() - start_time
        mem_kb = -1
    return elapsed, mem_kb


def run_binary_benchmarks(
    *,
    include_best_effort_runtime: bool = False,
    include_transpilation_only: bool = False,
) -> list[dict[str, int | float | str]]:
    """Ejecuta benchmarks de binarios y devuelve resultados serializables."""
    validate_backend_metadata(
        BINARY_BENCHMARK_METADATA,
        context="pcobra.cobra.benchmarks.binary_bench.BINARY_BENCHMARK_METADATA",
    )

    env = os.environ.copy()
    tmp_file = tempfile.NamedTemporaryFile(suffix=".toml", delete=False)
    tmp_file.close()
    env["COBRA_TOML"] = str(Path(tmp_file.name))

    results: list[dict[str, int | float | str]] = []
    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            co_file = Path(tmpdir) / "program.co"
            co_file.write_text(CODE, encoding="utf-8")
            selected_backends = list(
                executable_benchmark_backends(
                    BINARY_BENCHMARK_METADATA,
                    include_experimental=include_best_effort_runtime,
                )
            )
            if include_transpilation_only:
                selected_backends.extend(
                    target for target in ("wasm", "asm") if target in BINARY_BENCHMARK_METADATA
                )

            for backend in selected_backends:
                cfg = BINARY_BENCHMARK_METADATA[backend]
                src_file = Path(tmpdir) / f"program.{cfg['ext']}"
                transp_cmd = [
                    sys.executable,
                    "-m",
                    "pcobra.cobra.cli.cli",
                    "compilar",
                    str(co_file),
                    "--tipo",
                    backend,
                ]
                try:
                    out = subprocess.check_output(transp_cmd, env=env, text=True, timeout=SUBPROCESS_TIMEOUT)
                except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
                    continue
                out = re.sub(r"\x1b\[[0-9;]*m", "", out)
                lines = [
                    l
                    for l in out.splitlines()
                    if not l.startswith("DEBUG:") and not l.startswith("INFO:")
                ]
                if lines and lines[0].startswith("Código generado"):
                    lines = lines[1:]
                src_file.write_text("\n".join(lines), encoding="utf-8")

                compile_cmd = [arg.format(file=src_file, tmp=tmpdir) for arg in cfg["compile"]]
                try:
                    subprocess.check_call(compile_cmd, timeout=SUBPROCESS_TIMEOUT)
                except Exception:
                    continue

                run_cmd = [arg.format(file=src_file, tmp=tmpdir) for arg in cfg["run"]]
                if not shutil.which(run_cmd[0]) and not os.path.exists(run_cmd[0]):
                    continue
                elapsed, mem = run_and_measure(run_cmd, env)
                bin_path = Path(cfg["bin"].format(file=src_file, tmp=tmpdir))
                size = bin_path.stat().st_size if bin_path.exists() else 0
                results.append(
                    {
                        "backend": backend,
                        "time": round(elapsed, 4),
                        "memory_kb": mem,
                        "binary_size": size,
                    }
                )
    finally:
        os.unlink(tmp_file.name)

    return results


def main(argv: list[str] | None = None) -> int:
    """Punto de entrada CLI para benchmark de binarios."""
    parser = argparse.ArgumentParser(description="Benchmark de binarios por backend")
    parser.add_argument(
        "--include-best-effort-runtime",
        action="store_true",
        help="Incluye runtimes best-effort no públicos (go/java).",
    )
    parser.add_argument(
        "--include-transpilation-only",
        action="store_true",
        help="Incluye targets solo de transpilación (wasm/asm) bajo modo explícito best-effort.",
    )
    args = parser.parse_args(argv)

    results = run_binary_benchmarks(
        include_best_effort_runtime=args.include_best_effort_runtime,
        include_transpilation_only=args.include_transpilation_only,
    )
    payload = json.dumps(results, indent=2)
    Path("binary_bench.json").write_text(payload, encoding="utf-8")
    print(payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
