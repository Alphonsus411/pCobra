import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

import resource

CODE = """
var x = 0
mientras x <= 1000 :
    x = x + 1
fin
imprimir(x)
"""

BACKENDS = {
    "c": {
        "ext": "c",
        "compile": ["gcc", "{file}", "-O2", "-o", "{tmp}/prog_c"],
        "run": ["{tmp}/prog_c"],
        "bin": "{tmp}/prog_c",
    },
    "cpp": {
        "ext": "cpp",
        "compile": ["g++", "{file}", "-O2", "-o", "{tmp}/prog_cpp"],
        "run": ["{tmp}/prog_cpp"],
        "bin": "{tmp}/prog_cpp",
    },
    "rust": {
        "ext": "rs",
        "compile": ["rustc", "{file}", "-O", "-o", "{tmp}/prog_rs"],
        "run": ["{tmp}/prog_rs"],
        "bin": "{tmp}/prog_rs",
    },
}


def run_and_measure(cmd: list[str], env: dict[str, str] | None = None) -> tuple[float, int]:
    """Ejecuta *cmd* y devuelve (tiempo_en_segundos, memoria_en_kb)."""
    start_usage = resource.getrusage(resource.RUSAGE_CHILDREN)
    start_time = time.perf_counter()
    subprocess.run(cmd, env=env, check=False, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
    elapsed = time.perf_counter() - start_time
    end_usage = resource.getrusage(resource.RUSAGE_CHILDREN)
    mem_kb = max(0, end_usage.ru_maxrss - start_usage.ru_maxrss)
    return elapsed, mem_kb


def main() -> None:
    env = os.environ.copy()
    repo_root = Path(__file__).resolve().parents[2]
    env["PYTHONPATH"] = os.pathsep.join([
        str(repo_root / "backend"),
        str(repo_root / "src"),
    ])
    tmp_file = tempfile.NamedTemporaryFile(suffix=".toml", delete=False)
    tmp_file.close()
    env["PCOBRA_TOML"] = str(Path(tmp_file.name))

    results: list[dict[str, int | float | str]] = []
    with tempfile.TemporaryDirectory() as tmpdir:
        co_file = Path(tmpdir) / "program.co"
        co_file.write_text(CODE)
        for backend, cfg in BACKENDS.items():
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
                out = subprocess.check_output(transp_cmd, env=env, text=True)
            except subprocess.CalledProcessError:
                continue
            out = re.sub(r"\x1b\[[0-9;]*m", "", out)
            lines = [l for l in out.splitlines() if not l.startswith("DEBUG:") and not l.startswith("INFO:")]
            if lines and lines[0].startswith("Código generado"):
                lines = lines[1:]
            src_file.write_text("\n".join(lines))

            compile_cmd = [arg.format(file=src_file, tmp=tmpdir) for arg in cfg["compile"]]
            try:
                subprocess.check_call(compile_cmd)
            except Exception:
                continue

            run_cmd = [arg.format(file=src_file, tmp=tmpdir) for arg in cfg["run"]]
            if not shutil.which(run_cmd[0]) and not os.path.exists(run_cmd[0]):
                continue
            elapsed, mem = run_and_measure(run_cmd, env)
            bin_path = Path(cfg["bin"].format(file=src_file, tmp=tmpdir))
            size = bin_path.stat().st_size if bin_path.exists() else 0
            results.append({
                "backend": backend,
                "time": round(elapsed, 4),
                "memory_kb": mem,
                "binary_size": size,
            })
    Path("binary_bench.json").write_text(json.dumps(results, indent=2))
    os.unlink(tmp_file.name)
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
