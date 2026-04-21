from __future__ import annotations

import contextlib
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import Any

try:
    import resource
except ImportError:  # pragma: no cover - Windows
    resource = None  # type: ignore
    try:
        import psutil  # type: ignore
    except Exception:
        psutil = None  # type: ignore
else:
    psutil = None  # type: ignore

from pcobra.cobra.architecture.backend_policy import PUBLIC_BACKENDS
from pcobra.cobra.benchmarks.targets_policy import BENCHMARK_BACKEND_METADATA
from pcobra.cobra.cli.i18n import _
from pcobra.cobra.cli.target_policies import OFFICIAL_RUNTIME_TARGETS
from pcobra.cobra.cli.utils.messages import mostrar_error, mostrar_info
from pcobra.cobra.transpilers.target_utils import target_label
from pcobra.core.cobra_config import tiempo_max_transpilacion

ANSI_ESCAPE = re.compile(r"\x1b\[[0-9;]*m")
SUBPROCESS_TIMEOUT = tiempo_max_transpilacion()

BENCHMARK_CODE = """
var x = 0
mientras x <= 1000 :
    x = x + 1
fin
imprimir(x)
"""


def run_and_measure(cmd: list[str], env: dict[str, str] | None = None) -> tuple[float, int]:
    try:
        if resource is not None:
            start_usage = resource.getrusage(resource.RUSAGE_CHILDREN)
            start_time = time.perf_counter()
            subprocess.run(cmd, env=env, check=False, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT, timeout=SUBPROCESS_TIMEOUT)
            elapsed = time.perf_counter() - start_time
            end_usage = resource.getrusage(resource.RUSAGE_CHILDREN)
            mem_kb = max(0, end_usage.ru_maxrss - start_usage.ru_maxrss)
            return elapsed, mem_kb
        if psutil is not None:
            start_time = time.perf_counter()
            proc = psutil.Popen(cmd, env=env, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)  # type: ignore
            max_mem = 0
            while proc.poll() is None:
                with contextlib.suppress(Exception):
                    max_mem = max(max_mem, proc.memory_info().rss)  # type: ignore
                time.sleep(0.05)
            proc.wait(timeout=SUBPROCESS_TIMEOUT)
            return time.perf_counter() - start_time, max_mem // 1024

        start_time = time.perf_counter()
        subprocess.run(cmd, env=env, check=False, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT, timeout=SUBPROCESS_TIMEOUT)
        return time.perf_counter() - start_time, 0
    except subprocess.TimeoutExpired:
        mostrar_error(_("Timeout al ejecutar {cmd}").format(cmd=" ".join(cmd)))
        return 0.0, 0


def run_backend_benchmark(backend: str, cfg: dict[str, Any], co_file: Path, tmpdir: str, env: dict[str, str]) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    backend_display = f"{target_label(backend)} ({backend})" if backend in PUBLIC_BACKENDS else backend
    src_file = Path(tmpdir) / f"program.{cfg['ext']}"

    transp_cmd = [sys.executable, "-m", "pcobra.cobra.cli.cli", "compilar", str(co_file), "--tipo", backend]
    try:
        out = subprocess.check_output(transp_cmd, env=env, text=True)
    except subprocess.CalledProcessError as exc:
        mostrar_info(_("Error al compilar {backend}: {error}").format(backend=backend_display, error=str(exc)))
        return results

    out = ANSI_ESCAPE.sub("", out)
    lines = [line for line in out.splitlines() if not line.startswith(("DEBUG:", "INFO:"))]
    if lines and lines[0].startswith("Código generado"):
        lines = lines[1:]
    src_file.write_text("\n".join(lines))

    if "compile" in cfg:
        compile_cmd = [arg.format(file=src_file, tmp=tmpdir) for arg in cfg["compile"]]
        try:
            subprocess.run(compile_cmd, check=True, timeout=SUBPROCESS_TIMEOUT)
        except (subprocess.SubprocessError, subprocess.TimeoutExpired) as exc:
            mostrar_info(_("Error al compilar {backend}: {error}").format(backend=backend_display, error=str(exc)))
            return results

    cmd = [arg.format(file=src_file, tmp=tmpdir) for arg in cfg["run"]]
    if not shutil.which(cmd[0]) and not os.path.exists(cmd[0]):
        mostrar_info(_("Ejecutable no encontrado para {backend}: {cmd}").format(backend=backend_display, cmd=cmd[0]))
        return results

    elapsed, mem = run_and_measure(cmd, env)
    results.append({"backend": backend, "time": round(elapsed, 4), "memory_kb": mem})
    return results


def run_benchmarks(backends: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    env = os.environ.copy()
    results: list[dict[str, Any]] = []

    with tempfile.NamedTemporaryFile(suffix=".toml", delete=False) as tmp_file:
        tmp_path = Path(tmp_file.name)
        env["COBRA_TOML"] = str(tmp_path)

    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            co_file = Path(tmpdir) / "program.co"
            co_file.write_text(BENCHMARK_CODE)

            cobra_cmd = [sys.executable, "-m", "pcobra.cobra.cli.cli", "ejecutar", str(co_file)]
            elapsed, mem = run_and_measure(cobra_cmd, env)
            results.append({"backend": "cobra", "time": round(elapsed, 4), "memory_kb": mem})

            for backend, cfg in backends.items():
                results.extend(run_backend_benchmark(backend, cfg, co_file, tmpdir, env))
    finally:
        tmp_path.unlink(missing_ok=True)

    return results


def benchmark_backends_config(allowed_backends: set[str]) -> dict[str, dict[str, Any]]:
    return {
        backend: BENCHMARK_BACKEND_METADATA[backend]
        for backend in allowed_backends
        if backend in BENCHMARK_BACKEND_METADATA
    }


def cli_runtime_benchmark_backends() -> dict[str, dict[str, Any]]:
    """Backends de benchmark para CLI pública.

    Centraliza el estado compartido para evitar constantes globales en comandos.
    """
    return {
        target: BENCHMARK_BACKEND_METADATA[target]
        for target in OFFICIAL_RUNTIME_TARGETS
        if target in BENCHMARK_BACKEND_METADATA
    }
