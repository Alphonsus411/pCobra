from unittest.mock import patch
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from cobra.cli.cli import main


def test_cli_accepts_positional_argument_with_leading_dash():
    with patch("cobra.cli.cli.messages.mostrar_logo"), \
         patch("cobra.cli.commands.execute_cmd.ExecuteCommand.run", return_value=0) as mock_run:
        result = main(["ejecutar", "--", "-archivo.co"])
    assert result == 0
    args_passed = mock_run.call_args[0][0]
    assert args_passed.archivo == "-archivo.co"
