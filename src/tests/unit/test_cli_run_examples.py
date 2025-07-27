import os
import sys
import subprocess
from pathlib import Path
import pytest

ROOT = Path(__file__).resolve().parents[2]
EXAMPLES_DIR = ROOT / "examples"
EXPECTED_DIR = ROOT / "tests" / "data" / "expected_examples"

EXAMPLE_FILES = sorted(EXAMPLES_DIR.rglob("*.co"))


def _run_cli(args, toml_path):
    env = os.environ.copy()
    pythonpath = [str(ROOT)]
    if env.get("PYTHONPATH"):
        pythonpath.append(env["PYTHONPATH"])
    env["PYTHONPATH"] = os.pathsep.join(pythonpath)
    env["PCOBRA_TOML"] = str(toml_path)
    proc = subprocess.run(
        [sys.executable, "-m", "cli.cli", *args],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        env=env,
        text=True,
    )
    return proc.stdout


@pytest.mark.timeout(5)
@pytest.mark.parametrize("example", EXAMPLE_FILES, ids=[str(p.relative_to(EXAMPLES_DIR)) for p in EXAMPLE_FILES])
def test_examples_run(tmp_path, example):
    expected_file = EXPECTED_DIR / example.relative_to(EXAMPLES_DIR).with_suffix(".txt")
    toml = tmp_path / "empty.toml"
    toml.write_text("")
    output = _run_cli(["ejecutar", str(example)], toml)
    expected = ""
    if expected_file.exists():
        expected = expected_file.read_text().strip()
    assert output.strip() == expected
