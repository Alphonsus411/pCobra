from io import StringIO
from unittest.mock import patch
import pytest


@pytest.mark.timeout(5)
def test_cli_interactive():
    inputs = ["var x = 10", "imprimir(x)", "salir()"]
    expected_outputs = ["10"]

    with patch("builtins.input", side_effect=inputs), \
            patch("sys.stdout", new_callable=StringIO) as mock_stdout, \
            patch("cobra.cli.cli.messages.mostrar_logo"):
        from cobra.cli.cli import main
        main()

    output = mock_stdout.getvalue().strip().split("\n")
    assert output[0] == expected_outputs[0], f"Expected: {expected_outputs}, but got: {output}"


@pytest.mark.timeout(5)
def test_cli_transpilador():
    inputs = ["var x = 20", "imprimir(x)", "salir()"]
    expected_outputs = ["20"]

    with patch("builtins.input", side_effect=inputs), \
            patch("sys.stdout", new_callable=StringIO) as mock_stdout, \
            patch("cobra.cli.cli.messages.mostrar_logo"):
        from cobra.cli.cli import main
        main()

    output = mock_stdout.getvalue().strip().split("\n")
    assert output[0] == expected_outputs[0], f"Expected: {expected_outputs}, but got: {output}"
