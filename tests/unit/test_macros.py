from cobra.core import Lexer
from cobra.core import Parser
from cobra.transpilers.transpiler.to_python import TranspiladorPython
from cobra.transpilers.import_helper import get_standard_imports

IMPORTS = get_standard_imports("python")


def test_macro_python():
    codigo = "macro saludo { imprimir(1) } saludo()"
    tokens = Lexer(codigo).tokenizar()
    ast = Parser(tokens).parsear()
    resultado = TranspiladorPython().generate_code(ast)
    assert resultado == IMPORTS + "print(1)\n"
