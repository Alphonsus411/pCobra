"""Pruebas focales del instrumento de benchmarks, no baselines oficiales."""

import shutil
import subprocess
import sys
from pathlib import Path

import pytest

from scripts.benchmarks import run_benchmarks as runner

pytestmark = pytest.mark.skipif(
    sys.platform != "linux" or not Path("/usr/bin/time").is_file(),
    reason="El instrumento de benchmarks requiere Linux y GNU time",
)


def test_python_measurement():
    elapsed, memory = runner.run_and_measure([sys.executable, "-c", "print(1001)"])
    assert elapsed > 0
    assert memory > 0


@pytest.mark.skipif(shutil.which("node") is None, reason="Node.js no disponible")
def test_javascript_measurement():
    elapsed, memory = runner.run_and_measure(["node", "-e", "console.log(1001)"])
    assert elapsed > 0
    assert memory > 0


@pytest.mark.parametrize("source", ["print(1000)", "pass", "print('1001 extra')"])
def test_invalid_stdout(source):
    with pytest.raises(RuntimeError, match="Salida funcional inesperada"):
        runner.run_and_measure([sys.executable, "-c", source])


def test_nonzero_exit_even_with_correct_stdout():
    with pytest.raises(subprocess.CalledProcessError):
        runner.run_and_measure(
            [sys.executable, "-c", "print(1001); raise SystemExit(3)"]
        )


@pytest.mark.skipif(shutil.which("rustc") is None, reason="rustc no disponible")
def test_rust_measurement(tmp_path):
    source = tmp_path / "probe.rs"
    binary = tmp_path / "probe"
    source.write_text('fn main() { println!("1001"); }', encoding="utf-8")
    subprocess.run(
        ["rustc", str(source), "-O", "-o", str(binary)],
        check=True,
        timeout=120,
    )
    elapsed, memory = runner.run_and_measure([str(binary)])
    assert elapsed > 0
    assert memory > 0
