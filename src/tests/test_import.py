import pytest
from io import StringIO
from unittest.mock import patch

from src.core.lexer import Lexer
from src.core.parser import Parser
from src.core.interpreter import InterpretadorCobra
from src.core.transpiler.to_python import TranspiladorPython


@pytest.mark.timeout(5)
def test_import_interpreter(tmp_path):
    mod = tmp_path / "mod.cobra"
    mod.write_text("var dato = 5")

    codigo = f"import '{mod}'\nimprimir(dato)"
    tokens = Lexer(codigo).analizar_token()
    ast = Parser(tokens).parsear()
    interp = InterpretadorCobra()

    with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
        interp.ejecutar_ast(ast)

    assert mock_stdout.getvalue().strip() == "5"


@pytest.mark.timeout(5)
def test_import_transpiler(tmp_path):
    mod = tmp_path / "m.cobra"
    mod.write_text("var valor = 3")

    codigo = f"import '{mod}'\nimprimir(valor)"
    tokens = Lexer(codigo).analizar_token()
    ast = Parser(tokens).parsear()

    py_code = TranspiladorPython().transpilar(ast)
    expected = "valor = 3\nprint(valor)\n"
    assert py_code == expected

