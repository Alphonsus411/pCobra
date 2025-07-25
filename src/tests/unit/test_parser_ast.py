from cobra.lexico.lexer import Lexer
from cobra.parser.parser import Parser
from core.ast_nodes import NodoAsignacion, NodoValor


def test_parser_generates_ast_for_assignment():
    codigo = "var x = 5"
    tokens = Lexer(codigo).analizar_token()
    ast = Parser(tokens).parsear()
    assert len(ast) == 1
    nodo = ast[0]
    assert isinstance(nodo, NodoAsignacion)
    assert nodo.variable == "x"
    assert isinstance(nodo.expresion, NodoValor)
    assert nodo.expresion.valor == 5
