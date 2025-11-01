"""Pruebas para el nodo de tipos del AST de Cobra."""

from core import ast_nodes
from cobra.core.lexer import Token, TipoToken


def test_nodo_tipo_normaliza_nombre_y_genericos():
    nodo = ast_nodes.NodoTipo("Entero", genericos=("T1", "T2"))

    assert nodo.nombre == "Entero"
    assert nodo.genericos == ["T1", "T2"]


def test_nodo_tipo_acepta_tokens_y_copia_genericos():
    token = Token(TipoToken.IDENTIFICADOR, "Vector")
    original = ast_nodes.NodoTipo(token, genericos=["T"])

    copia = ast_nodes.NodoTipo(original)

    assert copia.nombre == "Vector"
    assert copia.genericos == ["T"]
    assert copia.genericos is not original.genericos
