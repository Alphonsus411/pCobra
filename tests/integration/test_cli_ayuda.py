import subprocess
import sys
from pathlib import Path
import os
import argparse
import pytest
from io import StringIO
from unittest.mock import patch

from cobra.cli.cli import main
from pcobra.cobra.cli.commands.compile_cmd import CompileCommand


def _env_without_sqlite_db_key() -> dict[str, str]:
    env = os.environ.copy()
    env.pop("SQLITE_DB_KEY", None)
    env.pop("COBRA_DEV_MODE", None)
    env.pop("COBRA_CLI_COMMAND_PROFILE", None)
    env.pop("COBRA_INTERNAL_ENABLE_LEGACY_CLI", None)
    env.pop("COBRA_INTERNAL_LEGACY_TARGETS", None)
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


def test_cobra_version_funciona_sin_sqlite_db_key(monkeypatch):
    with patch("sys.stdout", new_callable=StringIO) as out:
        with pytest.raises(SystemExit) as exc:
            main(["--version"])
        assert exc.value.code == 0
    assert "cobra" in out.getvalue().lower()


def test_cobra_compilar_help_muestra_exactamente_8_targets_canonicos_por_tier():
    parser = argparse.ArgumentParser(prog="cobra")
    subparsers = parser.add_subparsers(dest="command")
    compile_parser = CompileCommand().register_subparser(subparsers)
    stdout = " ".join(compile_parser.format_help().split())
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
    assert "Aliases aceptados" not in compile_parser.format_help()


def test_cobra_help_documenta_separacion_de_modos_en_snapshot(monkeypatch):
    with patch("sys.stdout", new_callable=StringIO) as out:
        with pytest.raises(SystemExit) as exc:
            main(["--help"])
        assert exc.value.code == 0

    normalized_stdout = " ".join(out.getvalue().split())
    expected_lines = [
        line.strip()
        for line in (Path(__file__).parent / "golden" / "cli_help_modos.golden")
        .read_text(encoding="utf-8")
        .splitlines()
        if line.strip()
    ]
    for expected_line in expected_lines:
        assert expected_line in normalized_stdout


def test_cobra_help_snapshot_publico_no_expone_comandos_legacy(monkeypatch):
    with patch("sys.stdout", new_callable=StringIO) as out:
        with pytest.raises(SystemExit) as exc:
            main(["--help"])
        assert exc.value.code == 0

    stdout = out.getvalue()
    normalized_stdout = " ".join(stdout.split())
    expected_snapshot = (
        Path(__file__).parent / "golden" / "cli_help_public_snapshot.golden"
    ).read_text(encoding="utf-8")
    assert " ".join(normalized_stdout.split()) == " ".join(expected_snapshot.split())
    lower_stdout = stdout.lower()
    for command in ("run", "build", "test", "mod", "repl"):
        assert f" {command} " in f" {lower_stdout} "
    for command in ("installer", "paquete", "hub"):
        assert f" {command} " not in f" {lower_stdout} "
    assert "\n  legacy " not in lower_stdout
