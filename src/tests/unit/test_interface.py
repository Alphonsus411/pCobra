from cobra.lexico.lexer import Lexer
from cobra.parser.parser import Parser
from core.ast_nodes import NodoInterface, NodoClase
from cobra.transpilers.transpiler.to_python import TranspiladorPython
from cobra.transpilers.transpiler.to_js import TranspiladorJavaScript
from cobra.transpilers.transpiler.to_cpp import TranspiladorCPP
from cobra.transpilers.transpiler.to_rust import TranspiladorRust

CODIGO = """
interface Printable:
    func mostrar()
fin
clase Doc(Printable):
    func mostrar():
        imprimir("doc")
    fin
fin
"""

def test_parser_interface():
    tokens = Lexer(CODIGO).tokenizar()
    ast = Parser(tokens).parsear()
    assert isinstance(ast[0], NodoInterface)
    assert isinstance(ast[1], NodoClase)
    assert ast[1].bases == ["Printable"]

def test_transpiladores_interface():
    tokens = Lexer("interface I:\n    func m()\nfin\n").tokenizar()
    ast = Parser(tokens).parsear()
    py = TranspiladorPython().generate_code(ast)
    assert "class I" in py
    js = TranspiladorJavaScript().generate_code(ast)
    assert "class I" in js
    cpp = TranspiladorCPP().generate_code(ast)
    assert "struct I" in cpp
    rs = TranspiladorRust().generate_code(ast)
    assert "trait I" in rs
