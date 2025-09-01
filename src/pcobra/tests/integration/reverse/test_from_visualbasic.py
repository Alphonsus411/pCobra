"""Pruebas de aceptación para el transpilador inverso de VisualBasic."""

from cobra.transpilers.reverse.from_visualbasic import ReverseFromVisualBasic
from core.ast_nodes import NodoAsignacion, NodoIdentificador, NodoValor


def test_reverse_from_visualbasic_assignment():
    code = "x = 42"
    ast = ReverseFromVisualBasic().generate_ast(code)
    assert len(ast) == 1
    nodo = ast[0]
    assert isinstance(nodo, NodoAsignacion)
    assert isinstance(nodo.variable, NodoIdentificador)
    assert nodo.variable.nombre == "x"
    assert isinstance(nodo.expresion, NodoValor)
    assert nodo.expresion.valor == 42

