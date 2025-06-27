import json
import os
import re
import subprocess
import sys
import tempfile
import time
from pathlib import Path
import resource

from .base import BaseCommand
from ..i18n import _
from ..utils.messages import mostrar_error, mostrar_info

CODE = """
var x = 0
mientras x <= 1000 :
    x = x + 1
fin
imprimir(x)
"""


def run_and_measure(cmd: list[str], env: dict[str, str] | None = None) -> tuple[float, int]:
    """Ejecuta *cmd* y devuelve (tiempo_en_segundos, memoria_en_kb)."""
    start_usage = resource.getrusage(resource.RUSAGE_CHILDREN)
    start_time = time.perf_counter()
    subprocess.run(cmd, env=env, check=False, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
    elapsed = time.perf_counter() - start_time
    end_usage = resource.getrusage(resource.RUSAGE_CHILDREN)
    mem_kb = max(0, end_usage.ru_maxrss - start_usage.ru_maxrss)
    return elapsed, mem_kb


class BenchmarksV2Command(BaseCommand):
    """Ejecuta benchmarks en varios modos."""

    name = "benchmarks2"

    def register_subparser(self, subparsers):
        parser = subparsers.add_parser(self.name, help=_("Ejecuta benchmarks nativos"))
        parser.add_argument(
            "--output",
            "-o",
            help=_("Archivo donde guardar el JSON con resultados"),
        )
        parser.set_defaults(cmd=self)
        return parser

    def run(self, args):
        env = os.environ.copy()
        env["PYTHONPATH"] = str(Path(__file__).resolve().parents[3])
        env["PCOBRA_TOML"] = str(Path(tempfile.mkstemp(suffix=".toml")[1]))
        env.pop("PYTEST_CURRENT_TEST", None)

        results = []
        with tempfile.TemporaryDirectory() as tmpdir:
            co_file = Path(tmpdir) / "program.co"
            co_file.write_text(CODE)

            # Modo nativo Cobra
            cmd = [sys.executable, "-m", "src.cli.cli", "ejecutar", str(co_file)]
            elapsed, mem = run_and_measure(cmd, env)
            results.append({"modo": "cobra", "time": round(elapsed, 4), "memory_kb": mem})

            # Transpilado a Python
            py_file = Path(tmpdir) / "program.py"
            transp_cmd = [
                sys.executable,
                "-m",
                "src.cli.cli",
                "compilar",
                str(co_file),
                "--tipo",
                "python",
            ]
            out = subprocess.check_output(transp_cmd, env=env, text=True)
            out = re.sub(r"\x1b\[[0-9;]*m", "", out)
            lines = [l for l in out.splitlines() if not l.startswith("DEBUG:") and not l.startswith("INFO:")]
            if lines and lines[0].startswith("Código generado"):
                lines = lines[1:]
            py_file.write_text("\n".join(lines))
            elapsed, mem = run_and_measure(["python", str(py_file)], env)
            results.append({"modo": "python", "time": round(elapsed, 4), "memory_kb": mem})

            # Transpilado a JavaScript
            js_file = Path(tmpdir) / "program.js"
            transp_cmd = [
                sys.executable,
                "-m",
                "src.cli.cli",
                "compilar",
                str(co_file),
                "--tipo",
                "js",
            ]
            out = subprocess.check_output(transp_cmd, env=env, text=True)
            out = re.sub(r"\x1b\[[0-9;]*m", "", out)
            lines = [l for l in out.splitlines() if not l.startswith("DEBUG:") and not l.startswith("INFO:")]
            if lines and lines[0].startswith("Código generado"):
                lines = lines[1:]
            js_file.write_text("\n".join(lines))
            elapsed, mem = run_and_measure(["node", str(js_file)], env)
            results.append({"modo": "js", "time": round(elapsed, 4), "memory_kb": mem})

            # Ejecución en sandbox
            runner = Path(tmpdir) / "run_sandbox.py"
            runner.write_text(
                "from src.core.sandbox import ejecutar_en_sandbox\n"
                "import pathlib, sys\n"
                "codigo = pathlib.Path(sys.argv[1]).read_text()\n"
                "ejecutar_en_sandbox(codigo)\n"
            )
            elapsed, mem = run_and_measure([sys.executable, str(runner), str(py_file)], env)
            results.append({"modo": "sandbox", "time": round(elapsed, 4), "memory_kb": mem})

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
