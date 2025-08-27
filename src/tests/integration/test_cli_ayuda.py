import subprocess
import sys
from pathlib import Path


def test_cobra_ayuda_equivalente_help():
    cli_path = Path(__file__).resolve().parents[2] / "cli.py"
    result_help = subprocess.run(
        [sys.executable, str(cli_path), "--help"], capture_output=True, text=True
    )
    assert result_help.returncode == 0
    result_ayuda = subprocess.run(
        [sys.executable, str(cli_path), "ayuda"], capture_output=True, text=True
    )
    assert result_ayuda.returncode == 0
    assert result_help.stdout == result_ayuda.stdout
