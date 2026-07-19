from unittest.mock import patch
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from pcobra.cobra.cli import cli as cli_module
from pcobra.cobra.cli.commands.execute_cmd import ExecuteCommand


def test_cli_accepts_positional_argument_with_leading_dash():
    with patch.object(cli_module, "resolve_command_profile", return_value="development"), \
         patch.object(cli_module.AppConfig, "BASE_COMMAND_CLASSES", [ExecuteCommand]), \
         patch.object(cli_module.messages, "mostrar_logo"), \
         patch.object(ExecuteCommand, "run", return_value=0) as mock_run:
        result = cli_module.main(["ejecutar", "--", "-archivo.co"])
    assert result == 0
    args_passed = mock_run.call_args[0][0]
    assert args_passed.archivo == "-archivo.co"
