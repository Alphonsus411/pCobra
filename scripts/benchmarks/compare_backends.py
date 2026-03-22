"""Benchmark script.

La política de targets se hereda de ``src/pcobra/cobra/transpilers/targets.py``
a través de ``scripts/benchmarks/targets_policy.py``.
"""

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
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

try:
    import resource
    psutil = None
except ImportError:
    resource = None
    try:
        import psutil  # manejar ResourceUsage con psutil
    except ImportError:  # pragma: no cover - psutil no está disponible
        psutil = None

# Si no hay 'resource' ni 'psutil', la memoria se informará como -1

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

def run_and_measure(cmd: list[str], env: dict[str, str] | None = None) -> tuple[float, int]:
    """Ejecuta *cmd* y devuelve ``(tiempo_en_segundos, memoria_en_kb)``.

    Si no se dispone de ``resource`` ni de ``psutil``, la memoria se reporta como
    ``-1``.
    """

    start_time = time.perf_counter()
    if resource is not None:
        start_usage = resource.getrusage(resource.RUSAGE_CHILDREN)
        subprocess.run(
            cmd,
            env=env,
            check=False,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.STDOUT,
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
        ps_proc = psutil.Process(proc.pid)
        peak = 0
        while proc.poll() is None:
            try:
                rss = ps_proc.memory_info().rss
            except psutil.Error:
                break
            peak = max(peak, rss)
            time.sleep(0.01)
        proc.wait()
        elapsed = time.perf_counter() - start_time
        mem_kb = peak // 1024
    else:
        subprocess.run(
            cmd,
            env=env,
            check=False,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.STDOUT,
        )
        elapsed = time.perf_counter() - start_time
        mem_kb = -1
    return elapsed, mem_kb


def main() -> None:
    try:
        parser = argparse.ArgumentParser(description="Compara distintos backends")
    except ImportError:
        print("Error: No se pudo importar el módulo argparse")
        sys.exit(1)
    parser.add_argument(
        "--output",
        "-o",
        help="Archivo donde guardar el JSON con resultados",
    )
    parser.add_argument(
        "--include-best-effort-runtime",
        "--include-experimental-runtime",
        dest="include_best_effort_runtime",
        action="store_true",
        help=(
            "Incluye runtimes best-effort no públicos (actualmente `go` y `java`). "
            "Los targets solo de transpilación sin runtime público (`wasm`, `asm`) siguen excluidos."
        ),
    )
    args = parser.parse_args()

    repo_root = REPO_ROOT
    validate_backend_metadata(BACKEND_METADATA, context="compare_backends")
    validate_local_targets_policy(repo_root)

    env = os.environ.copy()
    env["PYTHONPATH"] = str(repo_root / "src")
    tmp_file = tempfile.NamedTemporaryFile(suffix=".toml", delete=False)
    tmp_file.close()
    env["COBRA_TOML"] = str(Path(tmp_file.name))

    results = []
    with tempfile.TemporaryDirectory() as tmpdir:
        co_file = Path(tmpdir) / "program.co"
        co_file.write_text(CODE)

        # Ejecutar directamente con el intérprete Cobra
        cobra_cmd = [
            sys.executable,
            "-m",
            "cobra.cli.cli",
            "ejecutar",
            str(co_file),
        ]
        elapsed, mem = run_and_measure(cobra_cmd, env)
        results.append({"backend": "cobra", "time": round(elapsed, 4), "memory_kb": mem})

        for backend in executable_benchmark_backends(
            BACKEND_METADATA,
            include_experimental=args.include_best_effort_runtime,
        ):
            cfg = BACKEND_METADATA[backend]
            run_cmd = cfg["run"]
            src_file = Path(tmpdir) / f"program.{cfg['ext']}"
            transp_cmd = [
                sys.executable,
                "-m",
                "cobra.cli.cli",
                "compilar",
                str(co_file),
                "--tipo",
                backend,
            ]
            try:
                out = subprocess.check_output(transp_cmd, env=env, text=True)
            except subprocess.CalledProcessError:
                continue
            out = re.sub(r"\x1b\[[0-9;]*m", "", out)
            lines = [l for l in out.splitlines() if not l.startswith("DEBUG:") and not l.startswith("INFO:")]
            if lines and lines[0].startswith("Código generado"):
                lines = lines[1:]
            out = "\n".join(lines)
            src_file.write_text(out)
            if "compile" in cfg:
                compile_cmd = [arg.format(file=src_file, tmp=tmpdir) for arg in cfg["compile"]]
                try:
                    subprocess.check_call(compile_cmd)
                except Exception:
                    continue
            cmd = [arg.format(file=src_file, tmp=tmpdir) for arg in run_cmd]
            if not shutil.which(cmd[0]) and not os.path.exists(cmd[0]):
                continue
            elapsed, mem = run_and_measure(cmd, env)
            results.append({
                "backend": backend,
                "time": round(elapsed, 4),
                "memory_kb": mem,
                "runtime_policy": cfg.get("runtime_policy", "unknown"),
            })

    data = json.dumps(results, indent=2)
    if args.output:
        Path(args.output).write_text(data)
    else:
        print(data)
    os.unlink(tmp_file.name)


if __name__ == "__main__":
    main()
