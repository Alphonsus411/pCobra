import argparse
import os
import subprocess
import sys
from pathlib import Path

import cobra.cli.cli as cli_module
from pcobra.cobra.cli.public_command_policy import PUBLIC_COMMANDS


def _public_env() -> dict[str, str]:
    env = os.environ.copy()
    env.pop("SQLITE_DB_KEY", None)
    env.pop("COBRA_DEV_MODE", None)
    env.pop("COBRA_CLI_COMMAND_PROFILE", None)
    env.pop("COBRA_INTERNAL_ENABLE_LEGACY_CLI", None)
    env.pop("COBRA_INTERNAL_LEGACY_TARGETS", None)
    return env


def test_cli_public_commands_contract_is_stable():
    assert PUBLIC_COMMANDS == ("run", "build", "test", "mod", "repl")


def test_cli_public_commands_contract_keeps_repl_as_official_command():
    # `repl` debe permanecer en el contrato público oficial (no alias legacy).
    assert "repl" in PUBLIC_COMMANDS


def test_cli_ui_v2_registra_repl_oficial_y_no_alias_interactive_legacy():
    registry = cli_module.CommandRegistry()
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command")

    commands = registry.register_base_commands(
        subparsers,
        ui="v2",
        profile="public",
    )

    assert "repl" in commands
    assert commands["repl"].__class__.__name__ == "ReplCommandV2"
    assert "interactive" not in commands


def test_cli_help_public_contract_snapshot():
    repo_root = Path(__file__).resolve().parents[2]
    result = subprocess.run(
        [sys.executable, "-m", "cobra.cli.cli", "--help"],
        capture_output=True,
        text=True,
        cwd=str(repo_root),
        env=_public_env(),
    )
    assert result.returncode == 0

    expected_snapshot = (
        Path(__file__).parent / "golden" / "cli_ui_v2_help_public.golden"
    ).read_text(encoding="utf-8")
    assert " ".join(result.stdout.lower().split()) == " ".join(expected_snapshot.split())
    for command in ("run", "build", "test", "mod", "repl"):
        assert f" {command} " in f" {result.stdout.lower()} "
    assert "\n  menu " not in result.stdout.lower()
    assert "\n  legacy " not in result.stdout.lower()
    assert "--backend" not in result.stdout.lower()
    assert "--tipo" not in result.stdout.lower()
    assert "--tipos" not in result.stdout.lower()


def test_cli_build_help_public_contract_no_expone_flags_backend():
    repo_root = Path(__file__).resolve().parents[2]
    result = subprocess.run(
        [sys.executable, "-m", "cobra.cli.cli", "build", "--help"],
        capture_output=True,
        text=True,
        cwd=str(repo_root),
        env=_public_env(),
    )
    assert result.returncode == 0
    output = result.stdout.lower()
    assert "--backend" not in output
    assert "--target" not in output
    assert "--tipo" not in output
    assert "--tipos" not in output








def test_cli_help_public_contract_muestra_warning_migracion_en_comando_legacy():
    repo_root = Path(__file__).resolve().parents[2]
    result = subprocess.run(
        [sys.executable, "-m", "cobra.cli.cli", "compilar", "--help"],
        capture_output=True,
        text=True,
        cwd=str(repo_root),
        env=_public_env(),
    )
    assert result.returncode == 0
    lower_output = result.stderr.lower() + result.stdout.lower()
    assert "comando legacy 'compilar'" in lower_output
    assert "migración automática aplicada: use 'build'" in lower_output
    assert "sugerencia: cobra build <archivo.co>" in lower_output
