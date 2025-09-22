from pcobra.cobra.core.lexer import Lexer
from pcobra.cobra.core.parser import Parser
from pcobra.core.ast_nodes import (
    NodoAssert,
    NodoDel,
    NodoGlobal,
    NodoNoLocal,
    NodoLambda,
    NodoWith,
    NodoTryCatch,
    NodoDefer,
)


def test_parser_afirmar():
    ast = Parser(Lexer("afirmar 1").analizar_token()).parsear()
    assert isinstance(ast[0], NodoAssert)


def test_parser_lambda():
    ast = Parser(Lexer("lambda x: x").analizar_token()).parsear()
    assert isinstance(ast[0], NodoLambda)


def test_parser_defer_dentro_funcion():
    codigo = """
    func demo():
        defer limpiar()
        retorno 1
    fin
    """
    parser = Parser(Lexer(codigo).analizar_token())
    ast = parser.parsear()
    funcion = ast[0]
    assert getattr(parser, "advertencias", []) == []
    assert any(isinstance(nodo, NodoDefer) for nodo in funcion.cuerpo)


def test_parser_defer_fuera_de_funcion_generar_advertencia():
    parser = Parser(Lexer("defer limpiar()").analizar_token())
    ast = parser.parsear()
    assert isinstance(ast[0], NodoDefer)
    assert parser.advertencias
    assert "función o método" in parser.advertencias[0]
