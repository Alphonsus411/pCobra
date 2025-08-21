import argparse
from unittest.mock import MagicMock, patch

from cobra.cli.cli import CommandRegistry
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
