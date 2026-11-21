import argparse
import hashlib
import json
import os
import platform
import re
import shutil
import signal
import subprocess
import sys
import uuid
from pathlib import Path
from statistics import median
from tempfile import TemporaryDirectory

seeds = (7, 101, 4093)
compilador = """
import argparse, sys
from pathlib import Path
from pcobra.cobra.cli.commands import compile_cmd
assert Path(compile_cmd.__file__).is_relative_to(Path(sys.argv[3]))
raise SystemExit(compile_cmd.CompileCommand().run(argparse.Namespace(
    archivo=sys.argv[1], tipo=sys.argv[2], backend=None, tipos=None)))
"""
prefixes = {
    "python": "import sys\nbenchmark_seed = int(sys.argv[1])\n",
    "javascript": "const benchmark_seed = Number(process.argv[2]);\n",
    "rust": "let benchmark_seed: i32 = std::env::args().nth(1).unwrap().parse().unwrap();\n",
}

def expected(seed):
    for index in range(1, 257):
        seed = (seed * 33 + index) % 65521
    return str(seed)

def measure(sampler, command, seed, env, folder):
    metrics = folder / "metrics.txt"
    with subprocess.Popen([str(sampler), str(metrics), *command, str(seed)],
                          cwd=folder, env=env, text=True, stdout=subprocess.PIPE,
                          stderr=subprocess.PIPE, start_new_session=True) as process:
        try:
            stdout, stderr = process.communicate(timeout=20)
        except subprocess.TimeoutExpired:
            os.killpg(process.pid, signal.SIGKILL)
            process.communicate()
            raise
    actual = stdout.strip()
    if process.returncode or actual != expected(seed):
        raise RuntimeError(f"{command[0]} seed={seed}, exit={process.returncode}, "
                           f"stdout={actual!r}, stderr={stderr[:1000]}")
    seconds, peak_rss = metrics.read_text().split()
    elapsed = float(seconds)
    peak_rss_kib = int(peak_rss)
    if elapsed <= 0 or peak_rss_kib <= 0:
        raise RuntimeError(f"Invalid measurement for {command[0]}: {elapsed}, {peak_rss_kib}")
    return {"seed": seed, "stdout": actual, "seconds": elapsed,
            "peak_rss_kib": peak_rss_kib}

def main():
    parser = argparse.ArgumentParser(description="Diagnose benchmark execution for two commits.")
    parser.add_argument("--baseline", type=Path, required=True)
    parser.add_argument("--candidate", type=Path, required=True)
    parser.add_argument("--runtime", type=Path, required=True)
    parser.add_argument("--node", default="node")
    parser.add_argument("--rustc", default="rustc")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    runtime = args.runtime.resolve()
    sampler = runtime / "measure"
    source = runtime / "workload.cobra"
    lines = ["var x0 = benchmark_seed"]
    for index in range(1, 257):
        lines.extend([f"var t{index} = x{index - 1} * 33 + {index}",
                      f"var x{index} = t{index} % 65521"])
    source.write_text("\n".join([*lines, "imprimir(x256)"]) + "\n", encoding="utf-8")

    report = {}
    checkouts = (
        (args.baseline, "08820d6c3426d71359911006c76a6a7fb260cfa0"),
        (args.candidate, "56164e716a2d32b49b4bf18fc72068e49b2a614f"),
    )
    for checkout, expected_sha in checkouts:
        root = checkout.resolve()
        sha = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root, text=True).strip()
        if sha != expected_sha:
            raise RuntimeError(f"Expected {expected_sha} at {root}, found {sha}")
        report[sha] = rows = {}
        with TemporaryDirectory(dir=runtime) as temporary:
            folder = Path(temporary)
            shutil.copytree(root / "src/pcobra/core/nativos", folder / "nativos")
            (folder / "package.json").write_text('{"type":"module"}')
            env = dict(os.environ, PYTHONPATH=str(root / "src"), PYTHONUTF8="1",
                       PYTHONDONTWRITEBYTECODE="1", SQLITE_DB_KEY=uuid.uuid4().hex,
                       COBRA_DB_PATH=str(folder / "probe.sqlite"))
            for backend, ext, executable in [
                ("python", "py", sys.executable), ("javascript", "js", args.node),
                ("rust", "rs", None),
            ]:
                raw = subprocess.check_output(
                    [sys.executable, "-c", compilador, str(source), backend, str(root)],
                    cwd=root, env=env, text=True, timeout=60
                )
                generated = re.sub(r"\x1b\[[0-9;]*m", "", raw).splitlines()
                assert generated[0].startswith("Código generado"), generated[0]
                body = prefixes[backend] + "\n".join(generated[1:]) + "\n"
                if backend == "rust":
                    body = "mod corelibs {}\nmod standard_library {}\nfn main() {\n" + body + "}\n"
                target = folder / f"benchmark.{ext}"
                target.write_text(body, encoding="utf-8")
                if backend == "rust":
                    binary = folder / "benchmark"
                    subprocess.run([args.rustc, str(target), "-O", "-o", str(binary)],
                                   cwd=folder, check=True, capture_output=True, timeout=60)
                    command = [str(binary)]
                else:
                    command = [executable, str(target)]
                samples = [measure(sampler, command, seed, env, folder) for seed in seeds for _ in range(2)]
                rows[backend] = {"samples": samples,
                                 "median_seconds": median(row["seconds"] for row in samples),
                                 "median_peak_rss_kib": median(row["peak_rss_kib"] for row in samples),
                                 "generated_sha256": hashlib.sha256(target.read_bytes()).hexdigest()}
                print(sha[:7], backend, [expected(seed) for seed in seeds], flush=True)
    evidence = {
        "kind": "diagnostic",
        "platform": platform.platform(),
        "runner_image": {key: os.environ.get(key) for key in ("ImageOS", "ImageVersion")},
        "github": {key: os.environ.get(key) for key in (
            "GITHUB_REPOSITORY", "GITHUB_SHA", "GITHUB_RUN_ID", "GITHUB_RUN_ATTEMPT"
        )},
        "runtime": {
            "python": platform.python_version(),
            "node": subprocess.check_output([args.node, "--version"], text=True).strip(),
            "rustc": subprocess.check_output([args.rustc, "--version"], text=True).strip(),
        },
        "workload_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
        "node_lock_sha256": hashlib.sha256((runtime / "package-lock.json").read_bytes()).hexdigest(),
        "python_requirements_sha256": hashlib.sha256(
            (args.candidate / "requirements.txt").read_bytes()
        ).hexdigest(),
        "expected": {seed: expected(seed) for seed in seeds},
        "metrics": {
            "seconds": "wall time including startup, excluding transpilation and compilation",
            "peak_rss_kib": "Linux wait4 ru_maxrss for each benchmark process",
        },
        "commits": report,
    }
    args.output.write_text(json.dumps(evidence, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
