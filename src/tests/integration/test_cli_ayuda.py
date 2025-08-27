import subprocess
import sys
from pathlib import Path


def test_cobra_ayuda_equivalente_help():
    cli_dir = Path(__file__).resolve().parents[2]
    result_help = subprocess.run(
        [sys.executable, "-m", "cobra.cli.cli", "--help"],
        capture_output=True,
        text=True,
        cwd=str(cli_dir),
    )
    assert result_help.returncode == 0
    result_ayuda = subprocess.run(
        [sys.executable, "-m", "cobra.cli.cli", "--ayuda"],
        capture_output=True,
        text=True,
        cwd=str(cli_dir),
    )
    assert result_ayuda.returncode == 0
    assert result_help.stdout == result_ayuda.stdout
