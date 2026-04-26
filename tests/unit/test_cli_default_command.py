import argparse
from contextlib import ExitStack
import re
from unittest.mock import patch

import pytest

from cobra.cli.cli import CliApplication, InteractiveCommand, CustomArgumentParser, main
from pcobra.cobra.cli.commands.base import BaseCommand


class _DummyRunCommand(BaseCommand):
    name = "run"

    def register_subparser(self, subparsers):
        parser = subparsers.add_parser(self.name, help="Ejecuta script Cobra")
        parser.set_defaults(cmd=self)
        return parser

    def run(self, _args):
        return 0


class _DummyReplCommand(BaseCommand):
    name = "repl"

    def register_subparser(self, subparsers):
        parser = subparsers.add_parser(self.name, help="Inicia REPL público")
        parser.add_argument("--sandbox", action="store_true", help="Sandbox REPL")
        parser.set_defaults(cmd=self)
        return parser

    def run(self, _args):
        return 0


def _patch_cli_env(stack: ExitStack) -> None:
    stack.enter_context(patch("cobra.cli.cli.setup_gettext"))
    stack.enter_context(patch("cobra.cli.cli.InterpretadorCobra"))
    stack.enter_context(patch("cobra.cli.cli.autocomplete_available", return_value=False))
    stack.enter_context(patch("cobra.cli.cli.enable_autocomplete"))
    stack.enter_context(patch("cobra.cli.cli.messages.disable_colors"))
    stack.enter_context(patch("cobra.cli.cli.messages.mostrar_logo"))
    stack.enter_context(patch("cobra.cli.cli.descubrir_plugins", return_value=[]))
    stack.enter_context(patch("cobra.cli.cli.resolve_command_profile", return_value="development"))


def test_no_command_prints_help_and_does_not_run_default():
    with ExitStack() as stack:
        _patch_cli_env(stack)
        stack.enter_context(patch("cobra.cli.cli.AppConfig.BASE_COMMAND_CLASSES", [InteractiveCommand]))
        mock_run = stack.enter_context(patch("cobra.cli.cli.InteractiveCommand.run", return_value=0))
        mock_info = stack.enter_context(patch("cobra.cli.cli.messages.mostrar_info"))
        app = CliApplication()
        result = app.run([])
    mock_run.assert_not_called()
    mock_info.assert_called_once()
    assert "no se indicó ningún comando" in mock_info.call_args.args[0].lower()
    assert result == 1


def test_main_without_args_prints_help_and_returns_one():
    with ExitStack() as stack:
        _patch_cli_env(stack)
        stack.enter_context(patch("cobra.cli.cli.AppConfig.BASE_COMMAND_CLASSES", [InteractiveCommand]))
        stack.enter_context(patch("cobra.cli.cli.configure_encoding"))
        mock_run = stack.enter_context(patch("cobra.cli.cli.InteractiveCommand.run", return_value=0))
        mock_info = stack.enter_context(patch("cobra.cli.cli.messages.mostrar_info"))

        result = main([])

    mock_run.assert_not_called()
    mock_info.assert_called_once()
    assert result == 1


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


def test_parse_arguments_without_command_keeps_cmd_undefined():
    with ExitStack() as stack:
        _patch_cli_env(stack)
        stack.enter_context(patch("cobra.cli.cli.AppConfig.BASE_COMMAND_CLASSES", [InteractiveCommand]))
        first_app = CliApplication()
        first_app.initialize()
        first_args = first_app._parse_arguments([])
        assert getattr(first_args, "cmd", None) is None

    with ExitStack() as stack:
        _patch_cli_env(stack)
        stack.enter_context(patch("cobra.cli.cli.AppConfig.BASE_COMMAND_CLASSES", [InteractiveCommand]))
        second_app = CliApplication()
        second_app.initialize()
        second_args = second_app._parse_arguments([])
        assert getattr(second_args, "cmd", None) is None


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

    assert getattr(first_args, "cmd", None) is None
    assert getattr(second_args, "cmd", None) is None
    assert register_spy.call_count == 1
    assert add_subparsers_spy.call_count == 1


def test_run_is_reentrant_on_same_instance_without_command_conflict():
    with ExitStack() as stack:
        _patch_cli_env(stack)
        stack.enter_context(patch("cobra.cli.cli.AppConfig.BASE_COMMAND_CLASSES", [InteractiveCommand]))
        mock_run = stack.enter_context(patch("cobra.cli.cli.InteractiveCommand.run", return_value=0))
        app = CliApplication()
        app.initialize()

        register_spy = stack.enter_context(
            patch.object(
                app.command_registry,
                "register_base_commands",
                wraps=app.command_registry.register_base_commands,
            )
        )

        first_result = app.run([])
        second_result = app.run([])

    assert first_result == 1
    assert second_result == 1
    assert mock_run.call_count == 0
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


def test_help_principal_lista_repl_como_comando_publico(capsys):
    with ExitStack() as stack:
        _patch_cli_env(stack)
        stack.enter_context(
            patch("cobra.cli.cli.AppConfig.V2_COMMAND_CLASSES", [_DummyRunCommand, _DummyReplCommand])
        )
        stack.enter_context(patch("cobra.cli.cli.resolve_command_profile", return_value="public"))
        app = CliApplication()
        with pytest.raises(SystemExit) as excinfo:
            app.run(["--help"])
    assert excinfo.value.code == 0
    stdout = capsys.readouterr().out
    assert "repl" in stdout
    assert "run" in stdout


def test_cli_sin_argumentos_no_imprime_ayuda_detallada_de_subcomandos(capsys):
    with ExitStack() as stack:
        _patch_cli_env(stack)
        stack.enter_context(
            patch("cobra.cli.cli.AppConfig.V2_COMMAND_CLASSES", [_DummyRunCommand, _DummyReplCommand])
        )
        stack.enter_context(patch("cobra.cli.cli.resolve_command_profile", return_value="public"))
        app = CliApplication()
        result = app.run([])
    assert result == 1
    stdout = capsys.readouterr().out
    assert "no se indicó ningún comando" in stdout.lower()
    assert "run" not in stdout.lower()
    assert "repl" not in stdout.lower()
    assert "--sandbox" not in stdout


def test_public_help_no_expone_aliases_legacy_en_superficie_visible(capsys):
    with ExitStack() as stack:
        _patch_cli_env(stack)
        stack.enter_context(
            patch("cobra.cli.cli.AppConfig.V2_COMMAND_CLASSES", [_DummyRunCommand, _DummyReplCommand])
        )
        stack.enter_context(patch("cobra.cli.cli.resolve_command_profile", return_value="public"))
        app = CliApplication()
        with pytest.raises(SystemExit) as excinfo:
            app.run(["--help"])

    assert excinfo.value.code == 0
    stdout = capsys.readouterr().out.lower()
    assert "run" in stdout
    assert "repl" in stdout
    legacy_as_command = re.compile(r"^\s+(ejecutar|compilar|verificar|modulos)\b", re.MULTILINE)
    assert legacy_as_command.search(stdout) is None
