import pytest
from cobra.core import Lexer, Token, TipoToken
from cobra.core import Parser
from core.ast_nodes import (
    NodoPara,
    NodoImprimir,
    NodoValor,
    NodoBucleMientras,
    NodoOperacionBinaria,
    NodoIdentificador,
    NodoTryCatch,
    NodoThrow,
)


def crear_ast_para():
    return [
        NodoPara(
            "i",
            NodoValor("range(0, 3)"),
            [NodoImprimir(NodoValor("i"))],
        )
    ]


def crear_ast_mientras():
    condicion = NodoOperacionBinaria(
        NodoIdentificador("x"),
        Token(TipoToken.MENORQUE, "<"),
        NodoValor(5),
    )
    return [
        NodoBucleMientras(
            condicion,
            [NodoImprimir(NodoValor("x"))],
        )
    ]


def crear_ast_try_catch():
    return [
        NodoTryCatch(
            [NodoThrow(NodoValor("err"))],
            "e",
            [NodoImprimir(NodoValor("e"))],
        )
    ]


@pytest.mark.timeout(5)
def test_parser_para():
    codigo = """para i in range(0,3):\n    imprimir(i)\nfin"""
    tokens = Lexer(codigo).analizar_token()
    ast = Parser(tokens).parsear()
    assert repr(ast) == repr(crear_ast_para())


@pytest.mark.timeout(5)
def test_parser_mientras():
    codigo = """mientras x < 5:\n    imprimir(x)\nfin"""
    tokens = Lexer(codigo).analizar_token()
    ast = Parser(tokens).parsear()
    assert repr(ast) == repr(crear_ast_mientras())


@pytest.mark.timeout(5)
def test_parser_intentar_capturar():
    codigo = (
        "intentar:\n    lanzar 'err'\ncapturar e:\n    imprimir(e)\nfin"
    )
    tokens = Lexer(codigo).analizar_token()
    ast = Parser(tokens).parsear()
    assert repr(ast) == repr(crear_ast_try_catch())
