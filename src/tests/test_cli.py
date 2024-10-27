import pytest
from unittest.mock import patch
from io import StringIO


def test_cli_interactive():
    inputs = ["var x = 45", "imprimir(x)", "salir()"]
    expected_outputs = ["45\n"]  # Esperamos que imprima '45'

    with patch("builtins.input", side_effect=inputs), \
            patch("sys.stdout", new_callable=StringIO) as mock_stdout:
        from src.cli.cli import main
        main()

    # Captura la salida
    output = mock_stdout.getvalue().strip().split("\n")

    # Verifica la salida
    assert output == expected_outputs


def test_cli_transpilador():
    inputs = ["var x = 45", "imprimir(x)", "salir()"]
    expected_outputs = ["45\n"]  # Esperamos que imprima '45'

    with patch("builtins.input", side_effect=inputs), \
            patch("sys.stdout", new_callable=StringIO) as mock_stdout:
        from src.cli.cli import main
        main()

    # Captura la salida
    output = mock_stdout.getvalue().strip().split("\n")

    # Verifica la salida
    assert output == expected_outputs

