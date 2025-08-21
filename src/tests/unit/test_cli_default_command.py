from contextlib import ExitStack
from unittest.mock import patch

import pytest

from cobra.cli.cli import CliApplication, InteractiveCommand, CustomArgumentParser


def _patch_cli_env(stack: ExitStack) -> None:
    stack.enter_context(patch("cobra.cli.cli.setup_gettext"))
    stack.enter_context(patch("cobra.cli.cli.InterpretadorCobra"))
    stack.enter_context(patch("cobra.cli.cli.argcomplete.autocomplete"))
    stack.enter_context(patch("cobra.cli.cli.messages.disable_colors"))
    stack.enter_context(patch("cobra.cli.cli.messages.mostrar_logo"))
    stack.enter_context(patch("cobra.cli.cli.descubrir_plugins", return_value=[]))


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
