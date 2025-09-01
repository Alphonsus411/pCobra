import pytest
from io import StringIO
from unittest.mock import patch

from cobra.core import Lexer
from cobra.core import Parser
from core.interpreter import (
    InterpretadorCobra,
    MODULES_PATH,
    IMPORT_WHITELIST,
)
from cobra.transpilers.transpiler.to_python import TranspiladorPython
from cobra.transpilers.import_helper import get_standard_imports

IMPORTS = get_standard_imports("python")


@pytest.mark.timeout(5)
def test_import_interpreter(tmp_path):
    mod = tmp_path / "mod.co"
    mod.write_text("var dato = 5")

    IMPORT_WHITELIST.add(str(mod))

    codigo = f"import '{mod}'\nimprimir(dato)"
    tokens = Lexer(codigo).analizar_token()
    ast = Parser(tokens).parsear()
    interp = InterpretadorCobra()

    with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
        interp.ejecutar_ast(ast)

    IMPORT_WHITELIST.remove(str(mod))

    assert mock_stdout.getvalue().strip() == "5"


@pytest.mark.timeout(5)
def test_import_transpiler(tmp_path):
    mod = tmp_path / "m.co"
    mod.write_text("var valor = 3")

    codigo = f"import '{mod}'\nimprimir(valor)"
    tokens = Lexer(codigo).analizar_token()
    ast = Parser(tokens).parsear()

    py_code = TranspiladorPython().generate_code(ast)
    expected = IMPORTS + "valor = 3\nprint(valor)\n"
    assert py_code == expected

