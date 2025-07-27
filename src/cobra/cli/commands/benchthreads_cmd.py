import json
import os
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
import subprocess
import sys
import tempfile
import time
from pathlib import Path

from cobra.lexico.lexer import Lexer
from cobra.parser.parser import Parser
from core.interpreter import InterpretadorCobra
from jupyter_kernel import CobraKernel

from cobra.cli.commands.base import BaseCommand
from cobra.cli.i18n import _
from cobra.cli.utils.messages import mostrar_error, mostrar_info

SEQUENTIAL_CODE = """
funcion tarea(n):
    var x = 0
    mientras x < n:
        x = x + 1
    fin
fin

tarea(50000)
tarea(50000)
"""

THREAD_CODE = """
funcion tarea(n):
    var x = 0
    mientras x < n:
        x = x + 1
    fin
fin

hilo tarea(50000)
hilo tarea(50000)
"""


def _measure(func):
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
    else:  # pragma: no cover - resource not available
        if psutil is not None:
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

    def register_subparser(self, subparsers):
        """Registra los argumentos del subcomando."""
        parser = subparsers.add_parser(
            self.name, help=_("Benchmark de hilos en CLI y Jupyter")
        )
        parser.add_argument(
            "--output",
            "-o",
            help=_("Archivo donde guardar el JSON con resultados"),
        )
        parser.set_defaults(cmd=self)
        return parser

    def _run_cli(self, code: str, env: dict[str, str]) -> None:
        with tempfile.NamedTemporaryFile("w", suffix=".co", delete=False) as tmp:
            tmp.write(code)
            tmp.flush()
            cmd = [sys.executable, "-m", "cobra.cli.cli", "ejecutar", tmp.name]
            subprocess.run(
                cmd, env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
            )
        os.unlink(tmp.name)

    def _run_kernel(self, code: str) -> None:
        kernel = CobraKernel()
        kernel.do_execute(code, silent=True)

    def _run_sequential(self) -> None:
        interp = InterpretadorCobra()
        tokens = Lexer(SEQUENTIAL_CODE).tokenizar()
        ast = Parser(tokens).parsear()
        interp.ejecutar_ast(ast)

    def run(self, args):
        """Ejecuta la lógica del comando."""
        env = os.environ.copy()
        env["PYTHONPATH"] = str(Path(__file__).resolve().parents[4])
        tmp_file = tempfile.NamedTemporaryFile(suffix=".toml", delete=False)
        tmp_file.close()
        env["PCOBRA_TOML"] = str(Path(tmp_file.name))

        results = []

        elapsed, cpu, io = _measure(self._run_sequential)
        results.append(
            {
                "modo": "secuencial",
                "time": round(elapsed, 4),
                "cpu": round(cpu, 4),
                "io": io,
            }
        )

        elapsed, cpu, io = _measure(lambda: self._run_cli(THREAD_CODE, env))
        results.append(
            {
                "modo": "cli_hilos",
                "time": round(elapsed, 4),
                "cpu": round(cpu, 4),
                "io": io,
            }
        )

        elapsed, cpu, io = _measure(lambda: self._run_kernel(THREAD_CODE))
        results.append(
            {
                "modo": "kernel_hilos",
                "time": round(elapsed, 4),
                "cpu": round(cpu, 4),
                "io": io,
            }
        )

        data = json.dumps(results, indent=2)
        if args.output:
            try:
                Path(args.output).write_text(data)
                mostrar_info(
                    _("Resultados guardados en {file}").format(file=args.output)
                )
            except Exception as err:
                mostrar_error(
                    _("No se pudo escribir el archivo: {err}").format(err=err)
                )
                return 1
        else:
            print(data)
        os.unlink(tmp_file.name)
        return 0
