import json
import os
import re
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
from pathlib import Path

from src.cli.commands.base import BaseCommand
from src.cli.i18n import _
from src.cli.utils.messages import mostrar_error, mostrar_info

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
    "cpp": {
        "ext": "cpp",
        "compile": ["g++", "{file}", "-O2", "-o", "{tmp}/prog_cpp"],
        "run": ["{tmp}/prog_cpp"],
    },
    "go": {"ext": "go", "run": ["go", "run", "{file}"]},
    "ruby": {"ext": "rb", "run": ["ruby", "{file}"]},
    "rust": {
        "ext": "rs",
        "compile": ["rustc", "{file}", "-O", "-o", "{tmp}/prog_rs"],
        "run": ["{tmp}/prog_rs"],
    },
}


def run_and_measure(
    cmd: list[str], env: dict[str, str] | None = None
) -> tuple[float, int]:
    """Ejecuta *cmd* y devuelve (tiempo_en_segundos, memoria_en_kb)."""
    if resource is not None:
        start_usage = resource.getrusage(resource.RUSAGE_CHILDREN)
        start_time = time.perf_counter()
        subprocess.run(
            cmd, env=env, check=False, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT
        )
        elapsed = time.perf_counter() - start_time
        end_usage = resource.getrusage(resource.RUSAGE_CHILDREN)
        mem_kb = max(0, end_usage.ru_maxrss - start_usage.ru_maxrss)
        return elapsed, mem_kb
    else:  # pragma: no cover - resource not available
        if psutil is not None:
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
            proc.wait()
            elapsed = time.perf_counter() - start_time
            mem_kb = max_mem // 1024
            return elapsed, mem_kb
        else:
            start_time = time.perf_counter()
            subprocess.run(
                cmd, env=env, check=False, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT
            )
            elapsed = time.perf_counter() - start_time
            return elapsed, 0


class BenchmarksCommand(BaseCommand):
    """Compara el rendimiento de distintos backends."""

    name = "benchmarks"

    def register_subparser(self, subparsers):
        """Registra los argumentos del subcomando."""
        parser = subparsers.add_parser(self.name, help=_("Ejecuta benchmarks"))
        parser.add_argument(
            "--output",
            "-o",
            help=_("Archivo donde guardar el JSON con resultados"),
        )
        parser.set_defaults(cmd=self)
        return parser

    def run(self, args):
        """Ejecuta la lógica del comando."""
        env = os.environ.copy()
        env["PYTHONPATH"] = str(Path(__file__).resolve().parents[4])
        fd, tmp_path = tempfile.mkstemp(suffix=".toml")
        os.close(fd)
        env["PCOBRA_TOML"] = str(Path(tmp_path))

        results = []
        with tempfile.TemporaryDirectory() as tmpdir:
            co_file = Path(tmpdir) / "program.co"
            co_file.write_text(CODE)
            for backend, cfg in BACKENDS.items():
                run_cmd = cfg["run"]
                src_file = Path(tmpdir) / f"program.{cfg['ext']}"
                transp_cmd = [
                    sys.executable,
                    "-m",
                    "src.cli.cli",
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
                lines = [
                    line
                    for line in out.splitlines()
                    if not line.startswith("DEBUG:") and not line.startswith("INFO:")
                ]
                if lines and lines[0].startswith("Código generado"):
                    lines = lines[1:]
                out = "\n".join(lines)
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
        return 0
