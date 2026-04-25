import argparse
import logging
import sys
import types
from unittest.mock import MagicMock, patch

from cobra.cli.cli import AppConfig, CommandRegistry, PROFILE_DEVELOPMENT
from cobra.cli.commands.interactive_cmd import InteractiveCommand
from pcobra.cobra.cli.commands.base import BaseCommand
from pcobra.cobra.cli.services.command_factory import CommandClassRoute


def test_register_base_commands_includes_interactive():
    registry = CommandRegistry(MagicMock())
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()
    with patch('cobra.cli.cli.descubrir_plugins', return_value=[]):
        commands = registry.register_base_commands(subparsers, ui="v1", profile=PROFILE_DEVELOPMENT)
    assert 'interactive' in commands
    assert commands['interactive'].__class__.__name__ == InteractiveCommand.__name__


def test_get_default_command_returns_interactive():
    registry = CommandRegistry(MagicMock())
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()
    with patch('cobra.cli.cli.descubrir_plugins', return_value=[]):
        registry.register_base_commands(subparsers, ui="v1", profile=PROFILE_DEVELOPMENT)
    default_cmd = registry.get_default_command()
    assert default_cmd.__class__.__name__ == InteractiveCommand.__name__


def test_register_base_commands_uses_fallback_for_missing_default(monkeypatch, caplog):
    monkeypatch.setattr(AppConfig, 'DEFAULT_COMMAND', 'missing')
    registry = CommandRegistry(MagicMock())
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()
    with patch('cobra.cli.cli.descubrir_plugins', return_value=[]):
        with caplog.at_level(logging.WARNING):
            registry.register_base_commands(subparsers, ui="v1", profile=PROFILE_DEVELOPMENT)
    assert AppConfig.DEFAULT_COMMAND == 'missing'
    assert registry.default_command_name == 'interactive'
    assert "Default command 'missing' not found" in caplog.text


def test_command_registry_keeps_default_isolated_across_instances(monkeypatch):
    parser_one = argparse.ArgumentParser()
    parser_two = argparse.ArgumentParser()
    subparsers_one = parser_one.add_subparsers()
    subparsers_two = parser_two.add_subparsers()

    with patch('cobra.cli.cli.descubrir_plugins', return_value=[]):
        monkeypatch.setattr(AppConfig, 'DEFAULT_COMMAND', 'interactive')
        first_registry = CommandRegistry(MagicMock())
        first_registry.register_base_commands(subparsers_one, ui="v1", profile=PROFILE_DEVELOPMENT)
        monkeypatch.setattr(AppConfig, 'DEFAULT_COMMAND', 'missing')
        second_registry = CommandRegistry(MagicMock())
        second_registry.register_base_commands(subparsers_two, ui="v1", profile=PROFILE_DEVELOPMENT)

    assert first_registry.default_command_name == 'interactive'
    assert second_registry.default_command_name == 'interactive'
    assert AppConfig.DEFAULT_COMMAND == 'missing'


def test_register_base_commands_degrada_si_ruta_no_cumple_basecommand(monkeypatch, caplog):
    module_name = "tests.fake_cli_registry_routes"
    fake_module = types.ModuleType(module_name)

    class RunFalso(BaseCommand):
        name = "run"

        def register_subparser(self, subparsers):
            parser = subparsers.add_parser(self.name)
            parser.set_defaults(cmd=self)
            return parser

        def run(self, args):
            return 0

    class ComandoRoto:
        pass

    setattr(fake_module, "RunFalso", RunFalso)
    setattr(fake_module, "ComandoRoto", ComandoRoto)
    sys.modules[module_name] = fake_module

    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()
    registry = CommandRegistry(MagicMock())
    monkeypatch.setattr(
        AppConfig,
        "V2_COMMAND_ROUTES",
        [
            CommandClassRoute(module_name, "RunFalso"),
            CommandClassRoute(module_name, "ComandoRoto"),
        ],
    )
    monkeypatch.setattr(AppConfig, "V2_COMMAND_CLASSES", [])
    try:
        with patch('cobra.cli.cli.descubrir_plugins', return_value=[]):
            with caplog.at_level(logging.ERROR):
                commands = registry.register_base_commands(subparsers, ui="v2")
        assert "run" in commands
        assert "Contrato de comando inválido" in caplog.text
    finally:
        sys.modules.pop(module_name, None)
