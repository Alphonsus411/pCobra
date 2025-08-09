import pytest
from cobra.core import Lexer
from cobra.core import Parser
from core.ast_nodes import NodoAsignacion, NodoValor


def test_parser_variable_inferencia():
    codigo = "variable x := 5"
    tokens = Lexer(codigo).analizar_token()
    parser = Parser(tokens)
    ast = parser.parsear()
    assert isinstance(ast[0], NodoAsignacion)
    assert ast[0].variable == "x"
    assert ast[0].inferencia is True
    assert isinstance(ast[0].expresion, NodoValor)
    assert ast[0].expresion.valor == 5
