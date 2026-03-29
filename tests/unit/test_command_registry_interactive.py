import argparse
import logging
from unittest.mock import MagicMock, patch

from cobra.cli.cli import AppConfig, CommandRegistry
from cobra.cli.commands.interactive_cmd import InteractiveCommand


def test_register_base_commands_includes_interactive():
    registry = CommandRegistry(MagicMock())
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()
    with patch('cobra.cli.cli.descubrir_plugins', return_value=[]):
        commands = registry.register_base_commands(subparsers)
    assert 'interactive' in commands
    assert isinstance(commands['interactive'], InteractiveCommand)


def test_get_default_command_returns_interactive():
    registry = CommandRegistry(MagicMock())
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()
    with patch('cobra.cli.cli.descubrir_plugins', return_value=[]):
        registry.register_base_commands(subparsers)
    default_cmd = registry.get_default_command()
    assert isinstance(default_cmd, InteractiveCommand)


def test_register_base_commands_uses_fallback_for_missing_default(monkeypatch, caplog):
    monkeypatch.setattr(AppConfig, 'DEFAULT_COMMAND', 'missing')
    registry = CommandRegistry(MagicMock())
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()
    with patch('cobra.cli.cli.descubrir_plugins', return_value=[]):
        with caplog.at_level(logging.WARNING):
            registry.register_base_commands(subparsers)
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
        first_registry.register_base_commands(subparsers_one)
        monkeypatch.setattr(AppConfig, 'DEFAULT_COMMAND', 'missing')
        second_registry = CommandRegistry(MagicMock())
        second_registry.register_base_commands(subparsers_two)

    assert first_registry.default_command_name == 'interactive'
    assert second_registry.default_command_name == 'interactive'
    assert AppConfig.DEFAULT_COMMAND == 'missing'
