import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

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

# Configuración de cada backend: extensión y comandos de ejecución
BACKENDS = {
    "python": {
        "ext": "py",
        "run": ["python", "{file}"]
    },
    "js": {
        "ext": "js",
        "run": ["node", "{file}"]
    },
    "cpp": {
        "ext": "cpp",
        "compile": ["g++", "{file}", "-O2", "-o", "{tmp}/prog_cpp"],
        "run": ["{tmp}/prog_cpp"]
    },
    "go": {
        "ext": "go",
        "run": ["go", "run", "{file}"]
    },
    "ruby": {
        "ext": "rb",
        "run": ["ruby", "{file}"]
    },
    "rust": {
        "ext": "rs",
        "compile": ["rustc", "{file}", "-O", "-o", "{tmp}/prog_rs"],
        "run": ["{tmp}/prog_rs"]
    }
}


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
    env = os.environ.copy()
    env["PYTHONPATH"] = str(Path(__file__).resolve().parents[2] / "backend")
    tmp_file = tempfile.NamedTemporaryFile(suffix=".toml", delete=False)
    tmp_file.close()
    env["PCOBRA_TOML"] = str(Path(tmp_file.name))

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
            results.append({"backend": backend, "time": round(elapsed, 4), "memory_kb": mem})
    print(json.dumps(results, indent=2))
    os.unlink(tmp_file.name)


if __name__ == "__main__":
    main()
