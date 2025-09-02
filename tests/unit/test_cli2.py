import pytest
from io import StringIO
from unittest.mock import patch


@pytest.mark.timeout(5)
def test_cli_interactive():
    inputs = ["var x = 10", "imprimir(x)", "salir()"]
    expected_outputs = ["10"]

    with patch("builtins.input", side_effect=inputs), \
            patch("sys.stdout", new_callable=StringIO) as mock_stdout:
        from cobra.cli.cli import main
        main()

    output = mock_stdout.getvalue().strip().split("\n")
    assert expected_outputs == output[-len(expected_outputs):]


@pytest.mark.timeout(5)
def test_cli_transpilador():
    inputs = ["var y = 20", "imprimir(y)", "salir()"]
    expected_outputs = ["20"]

    with patch("builtins.input", side_effect=inputs), \
            patch("sys.stdout", new_callable=StringIO) as mock_stdout:
        from cobra.cli.cli import main
        main()

    output = mock_stdout.getvalue().strip().split("\n")
    assert expected_outputs == output[-len(expected_outputs):]


@pytest.mark.timeout(5)
def test_cli_with_holobit():
    inputs = ["var h = holobit([1.0, 2.0, 3.0])", "imprimir(h)", "salir()"]
    expected_outputs = ["[1.0, 2.0, 3.0]"]

    with patch("builtins.input", side_effect=inputs), \
            patch("sys.stdout", new_callable=StringIO) as mock_stdout:
        from cobra.cli.cli import main
        main()

    output = mock_stdout.getvalue().strip().split("\n")
    assert expected_outputs == output[-len(expected_outputs):]


@pytest.mark.timeout(5)
def test_cli_for_loop():
    pytest.skip("Los bucles 'para' no están soportados en modo interactivo")
