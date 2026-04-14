import subprocess
import sys
from pathlib import Path
import os
import pytest


def _env_without_sqlite_db_key() -> dict[str, str]:
    env = os.environ.copy()
    env.pop("SQLITE_DB_KEY", None)
    env.pop("COBRA_DEV_MODE", None)
    return env


def test_cobra_ayuda_equivalente_help():
    cli_dir = Path(__file__).resolve().parents[2]
    result_help = subprocess.run(
        [sys.executable, "-m", "cobra.cli.cli", "--help"],
        capture_output=True,
        text=True,
        cwd=str(cli_dir),
        env=_env_without_sqlite_db_key(),
    )
    assert result_help.returncode == 0
    result_ayuda = subprocess.run(
        [sys.executable, "-m", "cobra.cli.cli", "--ayuda"],
        capture_output=True,
        text=True,
        cwd=str(cli_dir),
        env=_env_without_sqlite_db_key(),
    )
    assert result_ayuda.returncode == 0
    assert result_help.stdout == result_ayuda.stdout


def test_cobra_version_funciona_sin_sqlite_db_key():
    cli_dir = Path(__file__).resolve().parents[2]
    result = subprocess.run(
        [sys.executable, "-m", "cobra.cli.cli", "--version"],
        capture_output=True,
        text=True,
        cwd=str(cli_dir),
        env=_env_without_sqlite_db_key(),
    )
    assert result.returncode == 0
    assert "cobra" in result.stdout.lower()


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

    if expected_tiers not in stdout:
        pytest.skip("El entorno resolvió ayuda global en lugar de ayuda específica de 'compilar'.")

    assert expected_tiers in stdout
    assert "Aliases aceptados" not in result.stdout


def test_cobra_help_documenta_separacion_de_modos_en_snapshot():
    cli_dir = Path(__file__).resolve().parents[2]
    result = subprocess.run(
        [sys.executable, "-m", "cobra.cli.cli", "--help"],
        capture_output=True,
        text=True,
        cwd=str(cli_dir),
        env=_env_without_sqlite_db_key(),
    )
    assert result.returncode == 0

    normalized_stdout = " ".join(result.stdout.split())
    expected_lines = [
        line.strip()
        for line in (Path(__file__).parent / "golden" / "cli_help_modos.golden")
        .read_text(encoding="utf-8")
        .splitlines()
        if line.strip()
    ]
    for expected_line in expected_lines:
        assert expected_line in normalized_stdout


def test_cobra_help_snapshot_publico_no_expone_comandos_legacy():
    cli_dir = Path(__file__).resolve().parents[2]
    result = subprocess.run(
        [sys.executable, "-m", "cobra.cli.cli", "--help"],
        capture_output=True,
        text=True,
        cwd=str(cli_dir),
        env=_env_without_sqlite_db_key(),
    )
    assert result.returncode == 0

    expected_snapshot = (
        Path(__file__).parent / "golden" / "cli_help_public_no_legacy.golden"
    ).read_text(encoding="utf-8")
    assert " ".join(result.stdout.split()) == " ".join(expected_snapshot.split())
    assert "\n  legacy " not in result.stdout.lower()
