import contextlib
import cProfile
import json
import os
import re
from typing import Any, Dict, List, Optional, Tuple
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
import shutil
import subprocess
import sys
import tempfile
import time
from argparse import ArgumentParser, _SubParsersAction
from pathlib import Path

from cobra.cli.commands.base import BaseCommand
from cobra.cli.i18n import _
from cobra.cli.utils.messages import mostrar_error, mostrar_info
from core.cobra_config import tiempo_max_transpilacion

# Constantes
ANSI_ESCAPE = re.compile(r"\x1b\[[0-9;]*m")
SUBPROCESS_TIMEOUT = tiempo_max_transpilacion()

CODE = """
var x = 0
mientras x <= 1000 :
    x = x + 1
fin
imprimir(x)
"""

BACKENDS = {
    "python": {"ext": "py", "run": ["python", "{file}"]},
    "js": {"ext": "js", "run": ["node", "{file}"]},
    "rust": {
        "ext": "rs",
        "compile": ["rustc", "{file}", "-O", "-o", "{tmp}/prog_rs"],
        "run": ["{tmp}/prog_rs"],
    },
}

def run_and_measure(
    cmd: List[str], env: Optional[Dict[str, str]] = None
) -> Tuple[float, int]:
    """Ejecuta un comando y mide su tiempo de ejecución y uso de memoria.

    Args:
        cmd: Lista de argumentos del comando a ejecutar
        env: Diccionario con variables de entorno

    Returns:
        Tupla con (tiempo_ejecución, memoria_kb)
    """
    try:
        if resource is not None:
            start_usage = resource.getrusage(resource.RUSAGE_CHILDREN)
            start_time = time.perf_counter()
            subprocess.run(
                cmd,
                env=env,
                check=False,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.STDOUT,
                timeout=SUBPROCESS_TIMEOUT
            )
            elapsed = time.perf_counter() - start_time
            end_usage = resource.getrusage(resource.RUSAGE_CHILDREN)
            mem_kb = max(0, end_usage.ru_maxrss - start_usage.ru_maxrss)
            return elapsed, mem_kb
        elif psutil is not None:
            start_time = time.perf_counter()
            proc = psutil.Popen(
                cmd,
                env=env,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.STDOUT,
            )  # type: ignore
            max_mem = 0
            while proc.poll() is None:
                try:
                    mem = proc.memory_info().rss  # type: ignore
                    max_mem = max(max_mem, mem)
                except Exception:  # pragma: no cover - process ended
                    break
                time.sleep(0.05)
            proc.wait(timeout=SUBPROCESS_TIMEOUT)
            elapsed = time.perf_counter() - start_time
            mem_kb = max_mem // 1024
            return elapsed, mem_kb
        else:
            start_time = time.perf_counter()
            subprocess.run(
                cmd,
                env=env,
                check=False,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.STDOUT,
                timeout=SUBPROCESS_TIMEOUT
            )
            elapsed = time.perf_counter() - start_time
            return elapsed, 0
    except subprocess.TimeoutExpired:
        mostrar_error(_("Timeout al ejecutar {cmd}").format(cmd=" ".join(cmd)))
        return 0.0, 0

class BenchCommand(BaseCommand):
    """Ejecuta benchmarks y opcionalmente los perfila."""

    name = "bench"

    def register_subparser(self, subparsers: _SubParsersAction) -> ArgumentParser:
        """Registra los argumentos del subcomando.

        Args:
            subparsers: Objeto para registrar subcomandos

        Returns:
            Parser configurado para este subcomando
        """
        parser = subparsers.add_parser(self.name, help=_("Ejecuta benchmarks"))
        parser.add_argument(
            "--profile", 
            action="store_true", 
            help=_("Activa el modo de profiling")
        )
        parser.set_defaults(cmd=self)
        return parser

    def _run_benchmarks(self) -> List[Dict[str, Any]]:
        """Ejecuta los benchmarks para todos los backends configurados.

        Returns:
            Lista de diccionarios con resultados de los benchmarks
        """
        env = os.environ.copy()
        env["PYTHONPATH"] = str(Path(__file__).resolve().parents[4])
        
        results = []
        with tempfile.NamedTemporaryFile(suffix=".toml", delete=False) as tmp_file:
            tmp_path = Path(tmp_file.name)
            env["PCOBRA_TOML"] = str(tmp_path)

        try:
            with tempfile.TemporaryDirectory() as tmpdir:
                co_file = Path(tmpdir) / "program.co"
                co_file.write_text(CODE)

                # Benchmark del intérprete Cobra
                cobra_cmd = [sys.executable, "-m", "cobra.cli.cli", "ejecutar", str(co_file)]
                elapsed, mem = run_and_measure(cobra_cmd, env)
                results.append(
                    {"backend": "cobra", "time": round(elapsed, 4), "memory_kb": mem}
                )

                # Benchmark de los backends
                for backend, cfg in BACKENDS.items():
                    results.extend(self._benchmark_backend(backend, cfg, co_file, tmpdir, env))
        finally:
            os.unlink(tmp_path)
            import gc
            gc.collect()

        return results

    def _benchmark_backend(
        self, 
        backend: str, 
        cfg: Dict[str, Any], 
        co_file: Path, 
        tmpdir: str, 
        env: Dict[str, str]
    ) -> List[Dict[str, Any]]:
        """Ejecuta benchmark para un backend específico.

        Args:
            backend: Nombre del backend
            cfg: Configuración del backend
            co_file: Archivo con código Cobra
            tmpdir: Directorio temporal
            env: Variables de entorno

        Returns:
            Lista con resultados del benchmark
        """
        results = []
        run_cmd = cfg["run"]
        src_file = Path(tmpdir) / f"program.{cfg['ext']}"
        
        # Compilar código
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
        except subprocess.CalledProcessError as e:
            mostrar_info(_("Error al compilar {backend}: {error}").format(
                backend=backend, error=str(e)
            ))
            return results

        # Procesar salida
        out = ANSI_ESCAPE.sub("", out)
        lines = [
            line
            for line in out.splitlines()
            if not line.startswith(("DEBUG:", "INFO:"))
        ]
        if lines and lines[0].startswith("Código generado"):
            lines = lines[1:]
        src_file.write_text("\n".join(lines))

        # Compilar si es necesario
        if "compile" in cfg:
            compile_cmd = [
                arg.format(file=src_file, tmp=tmpdir) for arg in cfg["compile"]
            ]
            try:
                subprocess.run(compile_cmd, check=True, timeout=SUBPROCESS_TIMEOUT)
            except (subprocess.SubprocessError, subprocess.TimeoutExpired) as e:
                mostrar_info(_("Error al compilar {backend}: {error}").format(
                    backend=backend, error=str(e)
                ))
                return results

        # Ejecutar
        cmd = [arg.format(file=src_file, tmp=tmpdir) for arg in run_cmd]
        if not shutil.which(cmd[0]) and not os.path.exists(cmd[0]):
            mostrar_info(_("Ejecutable no encontrado para {backend}: {cmd}").format(
                backend=backend, cmd=cmd[0]
            ))
            return results

        elapsed, mem = run_and_measure(cmd, env)
        results.append(
            {"backend": backend, "time": round(elapsed, 4), "memory_kb": mem}
        )
        return results

    def run(self, args: Any) -> int:
        """Ejecuta la lógica del comando.

        Args:
            args: Argumentos parseados del comando

        Returns:
            0 si la ejecución fue exitosa, 1 en caso de error
        """
        if not hasattr(args, 'profile'):
            mostrar_error(_("Argumentos inválidos"))
            return 1

        try:
            if args.profile:
                profiler = cProfile.Profile()
                with profiler:
                    results = self._run_benchmarks()
                Path("bench_results.json").write_text(json.dumps(results, indent=2))
                profiler.dump_stats("bench_results.prof")
                mostrar_info(_("Resultados guardados en bench_results.json"))
            else:
                results = self._run_benchmarks()
                print(json.dumps(results, indent=2))
            return 0
        except Exception as e:
            mostrar_error(_("Error durante la ejecución: {error}").format(error=str(e)))
            return 1