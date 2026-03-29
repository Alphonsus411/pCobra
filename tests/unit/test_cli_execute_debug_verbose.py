from unittest.mock import patch

from cobra.cli.cli import main


def test_cli_ejecutar_con_debug_despues_del_archivo():
    with patch("cobra.cli.cli.messages.mostrar_logo"), patch(
        "cobra.cli.commands.execute_cmd.ExecuteCommand.run", return_value=0
    ) as mock_run:
        result = main(["ejecutar", "archivo.cobra", "--debug"])

    assert result == 0
    args_passed = mock_run.call_args[0][0]
    assert args_passed.archivo == "archivo.cobra"
    assert args_passed.debug is True
    assert args_passed.verbose == 0


def test_cli_ejecutar_con_verbose_global():
    with patch("cobra.cli.cli.messages.mostrar_logo"), patch(
        "cobra.cli.commands.execute_cmd.ExecuteCommand.run", return_value=0
    ) as mock_run:
        result = main(["-v", "ejecutar", "archivo.cobra"])

    assert result == 0
    args_passed = mock_run.call_args[0][0]
    assert args_passed.archivo == "archivo.cobra"
    assert args_passed.debug is False
    assert args_passed.verbose == 1
