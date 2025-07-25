import pytest
from core.interpreter import InterpretadorCobra
from cobra.lexico.lexer import Token, TipoToken
from core.ast_nodes import (
    NodoOperacionBinaria,
    NodoOperacionUnaria,
    NodoValor,
)


def test_suma_tipos_incompatibles():
    inter = InterpretadorCobra()
    expr = NodoOperacionBinaria(NodoValor(1), Token(TipoToken.SUMA, '+'), NodoValor('a'))
    with pytest.raises(TypeError, match='No se puede sumar'):
        inter.evaluar_expresion(expr)


def test_and_tipos_incompatibles():
    inter = InterpretadorCobra()
    expr = NodoOperacionBinaria(NodoValor(1), Token(TipoToken.AND, '&&'), NodoValor(True))
    with pytest.raises(TypeError, match='requiere booleanos'):
        inter.evaluar_expresion(expr)


def test_not_tipo_incompatible():
    inter = InterpretadorCobra()
    expr = NodoOperacionUnaria(Token(TipoToken.NOT, '!'), NodoValor(1))
    with pytest.raises(TypeError, match='requiere booleano'):
        inter.evaluar_expresion(expr)
