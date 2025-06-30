from backend.src.cobra.lexico.lexer import Lexer
from backend.src.cobra.parser.parser import Parser
from backend.src.core.ast_nodes import NodoAsignacion, NodoValor


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
