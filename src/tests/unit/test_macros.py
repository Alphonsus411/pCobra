from cobra.lexico.lexer import Lexer
from cobra.parser.parser import Parser
from cobra.transpilers.transpiler.to_python import TranspiladorPython
from cobra.transpilers.transpiler.to_cpp import TranspiladorCPP
from cobra.transpilers.import_helper import get_standard_imports

IMPORTS = get_standard_imports("python")


def test_macro_python():
    codigo = "macro saludo { imprimir(1) } saludo()"
    tokens = Lexer(codigo).tokenizar()
    ast = Parser(tokens).parsear()
    resultado = TranspiladorPython().generate_code(ast)
    assert resultado == IMPORTS + "print(1)\n"


def test_macro_cpp():
    codigo = "macro inc { var x = 10 } inc()"
    tokens = Lexer(codigo).tokenizar()
    ast = Parser(tokens).parsear()
    resultado = TranspiladorCPP().generate_code(ast)
    assert resultado == "auto x = 10;"
