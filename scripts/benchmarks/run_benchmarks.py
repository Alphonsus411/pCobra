"""Benchmark script.

La política de targets se hereda de ``src/pcobra/cobra/transpilers/targets.py``
a través de ``scripts/benchmarks/targets_policy.py``.
"""

import argparse
import json
import os
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
from pcobra.cobra.build import backend_pipeline

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


def normalize_rust_program(code: str) -> str:
    """Envuelve un snippet Rust del transpilador para poder ejecutarlo.

    El backend Rust produce cuerpos de programa y conserva sus imports de
    ``crate::corelibs`` y ``crate::standard_library``. Para los benchmarks,
    que compilan un archivo temporal autónomo, se declaran módulos vacíos y
    se añade el punto de entrada sin alterar la salida del transpilador.
    """

    if "fn main(" in code:
        return code

    body = "\n".join(f"    {line}" if line else "" for line in code.splitlines())
    return (
        "mod corelibs {}\n"
        "mod standard_library {}\n\n"
        "fn main() {\n"
        f"{body}\n"
        "}\n"
    )


def transpilar_benchmark(co_file: Path, backend: str) -> str:
    """Genera código con el pipeline interno canónico para ``backend``.

    Los comandos públicos de la CLI no exponen selección de backend. Los
    benchmarks necesitan esa selección de forma explícita, por lo que usan el
    punto de entrada interno aprobado en lugar del comando histórico
    ``compilar``.
    """

    resultado = backend_pipeline.build(
        str(co_file),
        {
            "preferred_backend": backend,
            "source_file": str(co_file),
        },
    )
    backend_resuelto = str(resultado.get("backend", ""))
    if backend_resuelto != backend:
        raise RuntimeError(
            "El pipeline de benchmarks resolvió un backend distinto: "
            f"esperado={backend}; obtenido={backend_resuelto or '∅'}"
        )
    return str(resultado["code"])


def run_and_measure(
    cmd: list[str], env: dict[str, str] | None = None
) -> tuple[float, int]:
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


def write_results(results: list[dict[str, object]], output: Path | None) -> str:
    """Serializa mediciones y, si se solicita, conserva su JSON versionable."""

    payload = json.dumps(results, indent=2)
    if output is not None:
        output.write_text(payload + "\n", encoding="utf-8")
    return payload


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
    parser.add_argument(
        "--output",
        type=Path,
        help="Guarda las mediciones JSON en esta ruta además de imprimirlas.",
    )
    args = parser.parse_args()

    repo_root = REPO_ROOT
    validate_backend_metadata(BACKEND_METADATA, context="run_benchmarks")
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
            try:
                out = transpilar_benchmark(co_file, backend)
            except Exception:
                continue
            if backend == "rust":
                out = normalize_rust_program(out)
            src_file.write_text(out)
            if "compile" in cfg:
                compile_cmd = [
                    arg.format(file=src_file, tmp=tmpdir) for arg in cfg["compile"]
                ]
                try:
                    subprocess.check_call(compile_cmd)
                except Exception:
                    continue
            cmd = [arg.format(file=src_file, tmp=tmpdir) for arg in run_cmd]
            if not shutil.which(cmd[0]) and not os.path.exists(cmd[0]):
                continue
            elapsed, mem = run_and_measure(cmd, env)
            results.append(
                {"backend": backend, "time": round(elapsed, 4), "memory_kb": mem}
            )
    measured_backends = {result["backend"] for result in results}
    missing_backends = set(selected_backends) - measured_backends
    if not results or missing_backends:
        os.unlink(tmp_file.name)
        raise RuntimeError(
            "Los benchmarks no produjeron mediciones para todos los backends: "
            f"{', '.join(sorted(missing_backends))}."
        )
    print(write_results(results, args.output))
    os.unlink(tmp_file.name)


if __name__ == "__main__":
    main()
