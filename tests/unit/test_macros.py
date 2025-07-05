from src.cobra.lexico.lexer import Lexer
from src.cobra.parser.parser import Parser
from src.cobra.transpilers.transpiler.to_python import TranspiladorPython
from src.cobra.transpilers.transpiler.to_cpp import TranspiladorCPP


def test_macro_python():
    codigo = "macro saludo { imprimir(1) } saludo()"
    tokens = Lexer(codigo).tokenizar()
    ast = Parser(tokens).parsear()
    resultado = TranspiladorPython().generate_code(ast)
    assert resultado == "from src.core.nativos import *\nprint(1)\n"


def test_macro_cpp():
    codigo = "macro inc { var x = 10 } inc()"
    tokens = Lexer(codigo).tokenizar()
    ast = Parser(tokens).parsear()
    resultado = TranspiladorCPP().generate_code(ast)
    assert resultado == "auto x = 10;"
