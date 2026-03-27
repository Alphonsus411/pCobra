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


def test_cobra_compilar_help_muestra_exactamente_8_targets_canonicos_por_tier():
    cli_dir = Path(__file__).resolve().parents[2]
    result = subprocess.run(
        [sys.executable, "-m", "cobra.cli.cli", "compilar", "--help"],
        capture_output=True,
        text=True,
        cwd=str(cli_dir),
    )
    assert result.returncode == 0

    stdout = " ".join(result.stdout.split())
    expected_lines = [
        line.strip()
        for line in (Path(__file__).parent / "golden" / "cli_help_targets_by_tier.golden")
        .read_text(encoding="utf-8")
        .splitlines()
        if line.strip()
    ]
    expected_tiers = " ".join(expected_lines)

    assert expected_tiers in stdout
    assert "Aliases aceptados" not in result.stdout
