import json
import logging
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time
from typing import Any, Dict, List, Optional, Tuple, Union

try:
    import resource
except ImportError:  # pragma: no cover - Windows
    resource = None  # type: ignore
    try:
        import psutil  # type: ignore
    except ImportError:
        psutil = None  # type: ignore
        logging.warning("Ni resource ni psutil están disponibles - mediciones limitadas")
else:
    psutil = None  # type: ignore

from cobra.core import Lexer
from cobra.core import Parser
from core.interpreter import InterpretadorCobra
from jupyter_kernel import CobraKernel
from cobra.cli.commands.base import BaseCommand
from cobra.cli.i18n import _
from cobra.cli.utils.messages import mostrar_error, mostrar_info
from core.cobra_config import tiempo_max_transpilacion

# Constantes de configuración
PROCESS_TIMEOUT = tiempo_max_transpilacion()
MAX_RETRIES = 3

# Mover códigos de prueba a archivos separados
SEQUENTIAL_CODE = Path(__file__).parent / "data" / "sequential_code.co"
THREAD_CODE = Path(__file__).parent / "data" / "thread_code.co"

def _measure(func) -> Tuple[float, float, int]:
    """Mide tiempo, CPU y operaciones I/O de una función.
    
    Args:
        func: Función a medir
        
    Returns:
        Tupla con (tiempo_transcurrido, tiempo_cpu, operaciones_io)
    """
    if resource is not None:
        start_usage = resource.getrusage(resource.RUSAGE_SELF)
        start = time.perf_counter()
        func()
        elapsed = time.perf_counter() - start
        end_usage = resource.getrusage(resource.RUSAGE_SELF)
        cpu = (end_usage.ru_utime + end_usage.ru_stime) - (
            start_usage.ru_utime + start_usage.ru_stime
        )
        io = (end_usage.ru_inblock + end_usage.ru_oublock) - (
            start_usage.ru_inblock + start_usage.ru_oublock
        )
        return elapsed, cpu, io
    elif psutil is not None:
        proc = psutil.Process()
        cpu_start = proc.cpu_times().user + proc.cpu_times().system
        try:
            io_start = proc.io_counters().read_count + proc.io_counters().write_count
        except Exception:
            io_start = 0
        start = time.perf_counter()
        func()
        elapsed = time.perf_counter() - start
        cpu_end = proc.cpu_times().user + proc.cpu_times().system
        try:
            io_end = proc.io_counters().read_count + proc.io_counters().write_count
        except Exception:
            io_end = io_start
        cpu = cpu_end - cpu_start
        io = io_end - io_start
        return elapsed, cpu, io
    else:
        start = time.perf_counter()
        func()
        elapsed = time.perf_counter() - start
        return elapsed, 0.0, 0

class BenchThreadsCommand(BaseCommand):
    """Compara la ejecución secuencial y en hilos."""

    name = "benchthreads"

    def register_subparser(self, subparsers) -> Any:
        """Registra los argumentos del subcomando."""
        parser = subparsers.add_parser(
            self.name, help=_("Benchmark de hilos en CLI y Jupyter")
        )
        parser.add_argument(
            "--output",
            "-o",
            help=_("Archivo donde guardar el JSON con resultados"),
            type=Path
        )
        parser.set_defaults(cmd=self)
        return parser

    def _run_cli(self, code: str, env: Dict[str, str]) -> None:
        """Ejecuta código usando la CLI.
        
        Args:
            code: Código a ejecutar
            env: Variables de entorno
            
        Raises:
            subprocess.SubprocessError: Si falla la ejecución
        """
        tmp_name = None
        try:
            with tempfile.NamedTemporaryFile("w", suffix=".co", delete=False) as tmp:
                tmp.write(code)
                tmp.flush()
                tmp_name = tmp.name
                
            for _ in range(MAX_RETRIES):
                try:
                    subprocess.run(
                        [sys.executable, "-m", "cobra.cli.cli", "ejecutar", tmp_name],
                        env=env,
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL,
                        timeout=PROCESS_TIMEOUT,
                        check=True
                    )
                    break
                except subprocess.TimeoutExpired:
                    continue
                
        finally:
            if tmp_name and os.path.exists(tmp_name):
                try:
                    os.unlink(tmp_name)
                except OSError:
                    logging.warning(f"No se pudo eliminar {tmp_name}")

    def _run_kernel(self, code: str) -> None:
        """Ejecuta código usando el kernel de Jupyter."""
        kernel = CobraKernel()
        kernel.do_execute(code, silent=True)

    def _run_sequential(self) -> None:
        """Ejecuta código de forma secuencial."""
        interp = InterpretadorCobra()
        tokens = Lexer(SEQUENTIAL_CODE.read_text()).tokenizar()
        ast = Parser(tokens).parsear()
        interp.ejecutar_ast(ast)

    def run(self, args: Any) -> int:
        """Ejecuta la lógica del comando.
        
        Returns:
            int: 0 si todo ok, 1 si hay error
        """
        env = os.environ.copy()
        env["PYTHONPATH"] = str(Path(__file__).resolve().parents[4])

        tmp_file: Optional[Path] = None
        try:
            with tempfile.NamedTemporaryFile(suffix=".toml", delete=False) as f:
                tmp_file = Path(f.name)
            env["COBRA_TOML"] = str(tmp_file)

            results: List[Dict[str, Union[str, float, int]]] = []

            elapsed, cpu, io = _measure(self._run_sequential)
            results.append({
                "modo": "secuencial",
                "time": round(elapsed, 4),
                "cpu": round(cpu, 4),
                "io": io,
            })

            elapsed, cpu, io = _measure(lambda: self._run_cli(THREAD_CODE.read_text(), env))
            results.append({
                "modo": "cli_hilos", 
                "time": round(elapsed, 4),
                "cpu": round(cpu, 4),
                "io": io,
            })

            elapsed, cpu, io = _measure(lambda: self._run_kernel(THREAD_CODE.read_text()))
            results.append({
                "modo": "kernel_hilos",
                "time": round(elapsed, 4),
                "cpu": round(cpu, 4),
                "io": io,
            })

            data = json.dumps(results, indent=2)
            
            if args.output:
                try:
                    args.output.parent.mkdir(parents=True, exist_ok=True)
                    args.output.write_text(data)
                    mostrar_info(_("Resultados guardados en {file}").format(
                        file=args.output)
                    )
                except OSError as err:
                    mostrar_error(_("Error al escribir {file}: {err}").format(
                        file=args.output, err=err)
                    )
                    return 1
            else:
                print(data)
                
            return 0
            
        finally:
            if tmp_file and tmp_file.exists():
                try:
                    tmp_file.unlink()
                except OSError:
                    logging.warning(f"No se pudo eliminar {tmp_file}")