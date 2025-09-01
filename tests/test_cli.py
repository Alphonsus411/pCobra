import subprocess
import sys


def test_cli_ayuda() -> None:
    result = subprocess.run(
        [sys.executable, "-m", "pcobra.cli", "ayuda"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    salida = result.stdout.lower()
    assert "cobra" in salida or "uso" in salida or "usage" in salida


def test_cli_transpilar_help() -> None:
    result = subprocess.run(
        [sys.executable, "-m", "pcobra.cli", "transpilar", "--help"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    salida = result.stdout.lower()
    assert "transpilar" in salida or "uso" in salida or "usage" in salida

