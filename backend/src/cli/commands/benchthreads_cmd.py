import json
import os
import subprocess
import sys
import tempfile
import time
import resource
from pathlib import Path

from .base import BaseCommand
from ..i18n import _
from ..utils.messages import mostrar_error, mostrar_info
from jupyter_kernel import CobraKernel
from core.interpreter import InterpretadorCobra
from cobra.lexico.lexer import Lexer
from cobra.parser.parser import Parser


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


class BenchThreadsCommand(BaseCommand):
    """Compara la ejecución secuencial y en hilos."""

    name = "benchthreads"

    def register_subparser(self, subparsers):
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
            cmd = [sys.executable, "-m", "src.cli.cli", "ejecutar", tmp.name]
            subprocess.run(cmd, env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
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
        env = os.environ.copy()
        env["PYTHONPATH"] = str(Path(__file__).resolve().parents[2])
        env["PCOBRA_TOML"] = str(Path(tempfile.mkstemp(suffix=".toml")[1]))

        results = []

        elapsed, cpu, io = _measure(self._run_sequential)
        results.append({"modo": "secuencial", "time": round(elapsed, 4), "cpu": round(cpu, 4), "io": io})

        elapsed, cpu, io = _measure(lambda: self._run_cli(THREAD_CODE, env))
        results.append({"modo": "cli_hilos", "time": round(elapsed, 4), "cpu": round(cpu, 4), "io": io})

        elapsed, cpu, io = _measure(lambda: self._run_kernel(THREAD_CODE))
        results.append({"modo": "kernel_hilos", "time": round(elapsed, 4), "cpu": round(cpu, 4), "io": io})

        data = json.dumps(results, indent=2)
        if args.output:
            try:
                Path(args.output).write_text(data)
                mostrar_info(_("Resultados guardados en {file}").format(file=args.output))
            except Exception as err:
                mostrar_error(_("No se pudo escribir el archivo: {err}").format(err=err))
                return 1
        else:
            print(data)
        return 0

