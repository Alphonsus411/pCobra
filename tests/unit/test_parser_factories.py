import pytest
from cobra.lexico.lexer import Lexer, Token, TipoToken
from cobra.parser.parser import Parser
from core.ast_nodes import (
    NodoAsignacion,
    NodoCondicional,
    NodoFuncion,
    NodoImprimir,
    NodoLlamadaFuncion,
    NodoRetorno,
)


def parse_code(code: str):
    tokens = Lexer(code).analizar_token()
    parser = Parser(tokens)
    return parser.parsear()


def test_dispatch_asignacion():
    ast = parse_code('var x = 1')
    assert len(ast) == 1
    nodo = ast[0]
    assert isinstance(nodo, NodoAsignacion)
    assert nodo.variable == 'x'
    assert nodo.expresion.valor == 1


def test_dispatch_condicional():
    codigo = 'si 1 > 0 :\n    imprimir(1)\nfin'
    ast = parse_code(codigo)
    nodo = ast[0]
    assert isinstance(nodo, NodoCondicional)
    assert len(nodo.bloque_si) == 1
    assert isinstance(nodo.bloque_si[0], NodoImprimir)


def test_dispatch_funcion():
    tokens = [
        Token(TipoToken.FUNC, 'func'),
        Token(TipoToken.IDENTIFICADOR, 'sumar'),
        Token(TipoToken.LPAREN, '('),
        Token(TipoToken.IDENTIFICADOR, 'a'),
        Token(TipoToken.COMA, ','),
        Token(TipoToken.IDENTIFICADOR, 'b'),
        Token(TipoToken.RPAREN, ')'),
        Token(TipoToken.DOSPUNTOS, ':'),
        Token(TipoToken.RETORNO, 'retorno'),
        Token(TipoToken.IDENTIFICADOR, 'a'),
        Token(TipoToken.SUMA, '+'),
        Token(TipoToken.IDENTIFICADOR, 'b'),
        Token(TipoToken.FIN, 'fin'),
        Token(TipoToken.EOF, None),
    ]
    ast = Parser(tokens).parsear()
    nodo = ast[0]
    assert isinstance(nodo, NodoFuncion)
    assert nodo.nombre == 'sumar'
    assert nodo.parametros == ['a', 'b']
    assert isinstance(nodo.cuerpo[0], NodoRetorno)
