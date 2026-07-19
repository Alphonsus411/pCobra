from unittest.mock import patch

from pcobra.cobra.cli import cli as cli_module
from pcobra.cobra.cli.commands.execute_cmd import ExecuteCommand


def test_cli_ejecutar_con_debug_despues_del_archivo():
    with (
        patch.object(cli_module, "resolve_command_profile", return_value="development"),
        patch.object(cli_module.AppConfig, "BASE_COMMAND_CLASSES", [ExecuteCommand]),
        patch.object(cli_module.messages, "mostrar_logo"),
        patch.object(ExecuteCommand, "run", return_value=0) as mock_run,
    ):
        result = cli_module.main(["ejecutar", "archivo.cobra", "--debug"])

    assert result == 0
    args_passed = mock_run.call_args[0][0]
    assert args_passed.archivo == "archivo.cobra"
    assert args_passed.debug is True
    assert args_passed.verbose == 0


def test_cli_ejecutar_con_verbose_global():
    with (
        patch.object(cli_module, "resolve_command_profile", return_value="development"),
        patch.object(cli_module.AppConfig, "BASE_COMMAND_CLASSES", [ExecuteCommand]),
        patch.object(cli_module.messages, "mostrar_logo"),
        patch.object(ExecuteCommand, "run", return_value=0) as mock_run,
    ):
        result = cli_module.main(["-v", "ejecutar", "archivo.cobra"])

    assert result == 0
    args_passed = mock_run.call_args[0][0]
    assert args_passed.archivo == "archivo.cobra"
    assert args_passed.debug is False
    assert args_passed.verbose == 1
