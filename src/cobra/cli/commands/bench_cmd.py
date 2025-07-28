import cProfile
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

from cobra.cli.commands.base import BaseCommand
from cobra.cli.i18n import _
from cobra.cli.utils.messages import mostrar_info
from re import compile, search  # (o las funciones específicas que necesites)

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
    cmd: list[str], env: dict[str, str] | None = None
) -> tuple[float, int]:
    if resource is not None:
        start_usage = resource.getrusage(resource.RUSAGE_CHILDREN)
        start_time = time.perf_counter()
        subprocess.run(
            cmd,
            env=env,
            check=False,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.STDOUT,
        )  # nosec B603
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
                cmd,
                env=env,
                check=False,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.STDOUT,
            )  # nosec B603
            elapsed = time.perf_counter() - start_time
            return elapsed, 0


class BenchCommand(BaseCommand):
    """Ejecuta benchmarks y opcionalmente los perfila."""

    name = "bench"

    def register_subparser(self, subparsers):
        """Registra los argumentos del subcomando."""
        parser = subparsers.add_parser(self.name, help=_("Ejecuta benchmarks"))
        parser.add_argument(
            "--profile", action="store_true", help=_("Activa el modo de profiling")
        )
        parser.set_defaults(cmd=self)
        return parser

    def _run_benchmarks(self) -> list[dict[str, object]]:
        env = os.environ.copy()
        env["PYTHONPATH"] = str(Path(__file__).resolve().parents[4])
        tmp_file = tempfile.NamedTemporaryFile(suffix=".toml", delete=False)
        tmp_file.close()
        env["PCOBRA_TOML"] = str(Path(tmp_file.name))

        results = []
        with tempfile.TemporaryDirectory() as tmpdir:
            co_file = Path(tmpdir) / "program.co"
            co_file.write_text(CODE)

            cobra_cmd = [sys.executable, "-m", "cobra.cli.cli", "ejecutar", str(co_file)]
            elapsed, mem = run_and_measure(cobra_cmd, env)
            results.append(
                {"backend": "cobra", "time": round(elapsed, 4), "memory_kb": mem}
            )

            for backend, cfg in BACKENDS.items():
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
                    out = subprocess.check_output(
                        transp_cmd, env=env, text=True
                    )  # nosec B603
                except subprocess.CalledProcessError:
                    continue  # nosec B112
                out = re.sub(r"\x1b\[[0-9;]*m", "", out)
                lines = [
                    line
                    for line in out.splitlines()
                    if not line.startswith("DEBUG:") and not line.startswith("INFO:")
                ]
                if lines and lines[0].startswith("Código generado"):
                    lines = lines[1:]
                src_file.write_text("\n".join(lines))
                if "compile" in cfg:
                    compile_cmd = [
                        arg.format(file=src_file, tmp=tmpdir) for arg in cfg["compile"]
                    ]
                    try:
                        subprocess.check_call(compile_cmd)  # nosec B603
                    except Exception:
                        continue  # nosec B112
                cmd = [arg.format(file=src_file, tmp=tmpdir) for arg in run_cmd]
                if not shutil.which(cmd[0]) and not os.path.exists(cmd[0]):
                    continue
                elapsed, mem = run_and_measure(cmd, env)
                results.append(
                    {"backend": backend, "time": round(elapsed, 4), "memory_kb": mem}
                )
        os.unlink(tmp_file.name)
        return results

    def run(self, args):
        """Ejecuta la lógica del comando."""
        if args.profile:
            profiler = cProfile.Profile()
            profiler.enable()
            results = self._run_benchmarks()
            profiler.disable()
            Path("bench_results.json").write_text(json.dumps(results, indent=2))
            profiler.dump_stats("bench_results.prof")
            mostrar_info(_("Resultados guardados en bench_results.json"))
        else:
            results = self._run_benchmarks()
            print(json.dumps(results, indent=2))
        return 0