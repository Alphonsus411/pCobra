import argparse
from contextlib import ExitStack
from unittest.mock import patch

import pytest

from cobra.cli.cli import CliApplication, InteractiveCommand, CustomArgumentParser, AppConfig, CommandRegistry


def _patch_cli_env(stack: ExitStack) -> None:
    stack.enter_context(patch("cobra.cli.cli.setup_gettext"))
    stack.enter_context(patch("cobra.cli.cli.InterpretadorCobra"))
    stack.enter_context(patch("cobra.cli.cli.autocomplete_available", return_value=False))
    stack.enter_context(patch("cobra.cli.cli.enable_autocomplete"))
    stack.enter_context(patch("cobra.cli.cli.messages.disable_colors"))
    stack.enter_context(patch("cobra.cli.cli.messages.mostrar_logo"))
    stack.enter_context(patch("cobra.cli.cli.descubrir_plugins", return_value=[]))
    stack.enter_context(patch("cobra.cli.cli.resolve_command_profile", return_value="development"))


def test_default_command_runs_interactive():
    with ExitStack() as stack:
        _patch_cli_env(stack)
        stack.enter_context(patch("cobra.cli.cli.AppConfig.BASE_COMMAND_CLASSES", [InteractiveCommand]))
        mock_run = stack.enter_context(patch("cobra.cli.cli.InteractiveCommand.run", return_value=0))
        app = CliApplication()
        result = app.run([])
    mock_run.assert_called_once()
    assert result == 0


def test_unknown_command_shows_error_and_help():
    with ExitStack() as stack:
        _patch_cli_env(stack)
        stack.enter_context(patch("cobra.cli.cli.AppConfig.BASE_COMMAND_CLASSES", [InteractiveCommand]))
        mock_error = stack.enter_context(patch("cobra.cli.utils.argument_parser.messages.mostrar_error"))
        mock_help = stack.enter_context(patch.object(CustomArgumentParser, "print_help"))
        app = CliApplication()
        with pytest.raises(SystemExit) as excinfo:
            app.run(["desconocido"])
    assert excinfo.value.code == 2
    mock_help.assert_called()
    mock_error.assert_called()


def test_consecutive_initializations_keep_default_command_isolated():
    with ExitStack() as stack:
        _patch_cli_env(stack)
        stack.enter_context(patch("cobra.cli.cli.AppConfig.BASE_COMMAND_CLASSES", [InteractiveCommand]))
        stack.enter_context(patch("cobra.cli.cli.AppConfig.DEFAULT_COMMAND", "interactive"))
        first_app = CliApplication()
        first_app.initialize()
        first_args = first_app._parse_arguments([])
        assert first_args.cmd.name == "interactive"

    with ExitStack() as stack:
        _patch_cli_env(stack)
        stack.enter_context(patch("cobra.cli.cli.AppConfig.BASE_COMMAND_CLASSES", [InteractiveCommand]))
        stack.enter_context(patch("cobra.cli.cli.AppConfig.DEFAULT_COMMAND", "missing"))
        second_app = CliApplication()
        second_app.initialize()
        second_args = second_app._parse_arguments([])
        assert second_args.cmd.name == "interactive"
        assert AppConfig.DEFAULT_COMMAND == "missing"


def test_parse_arguments_is_reentrant_on_same_instance():
    with ExitStack() as stack:
        _patch_cli_env(stack)
        stack.enter_context(patch("cobra.cli.cli.AppConfig.BASE_COMMAND_CLASSES", [InteractiveCommand]))
        app = CliApplication()
        app.initialize()

        register_spy = stack.enter_context(
            patch.object(app.command_registry, "register_base_commands", wraps=app.command_registry.register_base_commands)
        )
        add_subparsers_spy = stack.enter_context(
            patch.object(app.parser, "add_subparsers", wraps=app.parser.add_subparsers)
        )

        first_args = app._parse_arguments([])
        second_args = app._parse_arguments([])

    assert first_args.cmd.name == "interactive"
    assert second_args.cmd.name == "interactive"
    assert register_spy.call_count == 1
    assert add_subparsers_spy.call_count == 1


def test_run_is_reentrant_on_same_instance_without_command_conflict():
    with ExitStack() as stack:
        _patch_cli_env(stack)
        stack.enter_context(patch("cobra.cli.cli.AppConfig.BASE_COMMAND_CLASSES", [InteractiveCommand]))
        mock_run = stack.enter_context(patch("cobra.cli.cli.InteractiveCommand.run", return_value=0))
        app = CliApplication()

        register_spy = stack.enter_context(
            patch(
                "cobra.cli.cli.CommandRegistry.register_base_commands",
                autospec=True,
                wraps=CommandRegistry.register_base_commands,
            )
        )

        first_result = app.run([])
        second_result = app.run([])

    assert first_result == 0
    assert second_result == 0
    assert mock_run.call_count == 2
    assert register_spy.call_count == 1


def test_execute_command_without_parser_returns_controlled_error():
    with ExitStack() as stack:
        _patch_cli_env(stack)
        stack.enter_context(patch("cobra.cli.cli.AppConfig.BASE_COMMAND_CLASSES", [InteractiveCommand]))
        mock_error = stack.enter_context(patch("cobra.cli.cli.messages.mostrar_error"))
        app = CliApplication()
        app.initialize()
        app.parser = None

        result = app.execute_command(argparse.Namespace(cmd=None, lang="es"))

    assert result == 1
    mock_error.assert_called_once()
    assert "parser no disponible" in mock_error.call_args.args[0].lower()
