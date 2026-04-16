import argparse
import sys
from io import StringIO
from pathlib import Path
from unittest.mock import patch

import pytest

import cobra.cli.cli as cli_module
from cobra.cli.cli import main


@pytest.fixture(autouse=True)
def _stub_gettext(monkeypatch):
    monkeypatch.setattr(cli_module, "setup_gettext", lambda _lang=None: (lambda msg: msg))


def _normalizar(texto: str) -> str:
    return " ".join(texto.split())


def test_cli_ui_v2_help_snapshot_publico_no_expone_legacy():
    with patch("sys.stdout", new_callable=StringIO) as out:
        with pytest.raises(SystemExit) as exc:
            main(["--ui", "v2", "--help"])
    assert exc.value.code == 0
    texto = out.getvalue().lower()
    expected_snapshot = (
        Path(__file__).parent / "golden" / "cli_ui_v2_help_public.golden"
    ).read_text(encoding="utf-8")
    assert _normalizar(texto) == _normalizar(expected_snapshot)
    assert "\n  legacy " not in texto


def test_cli_ui_v2_help_muestra_legacy_solo_con_flag_interno(monkeypatch):
    monkeypatch.setenv("COBRA_INTERNAL_ENABLE_LEGACY_CLI", "1")
    for module_name in (
        "cobra.cli.commands_v2",
        "pcobra.cobra.cli.commands_v2",
        "cobra.cli.cli",
        "pcobra.cobra.cli.cli",
    ):
        sys.modules.pop(module_name, None)
    import cobra.cli.cli as cli_reloaded
    registry = cli_reloaded.CommandRegistry()
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command")
    commands = registry.register_base_commands(subparsers, ui="v2", profile="development")
    assert "legacy" in commands


def test_cli_ui_v2_sin_flag_no_registra_legacy(monkeypatch):
    monkeypatch.delenv("COBRA_INTERNAL_ENABLE_LEGACY_CLI", raising=False)
    for module_name in (
        "cobra.cli.commands_v2",
        "pcobra.cobra.cli.commands_v2",
        "cobra.cli.cli",
        "pcobra.cobra.cli.cli",
    ):
        sys.modules.pop(module_name, None)
    import cobra.cli.cli as cli_reloaded
    registry = cli_reloaded.CommandRegistry()
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command")
    commands = registry.register_base_commands(subparsers, ui="v2")
    assert "legacy" not in commands


def test_cli_ui_v2_modo_desarrollo_no_expone_legacy_sin_flag_interno(monkeypatch):
    monkeypatch.delenv("COBRA_INTERNAL_ENABLE_LEGACY_CLI", raising=False)
    monkeypatch.setenv("COBRA_DEV_MODE", "1")
    for module_name in (
        "cobra.cli.commands_v2",
        "pcobra.cobra.cli.commands_v2",
        "cobra.cli.cli",
        "pcobra.cobra.cli.cli",
    ):
        sys.modules.pop(module_name, None)
    import cobra.cli.cli as cli_reloaded

    registry = cli_reloaded.CommandRegistry()
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command")
    commands = registry.register_base_commands(
        subparsers,
        ui="v2",
        profile=cli_reloaded.resolve_command_profile(),
    )

    assert "legacy" not in commands
