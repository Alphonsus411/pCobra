"""Pruebas para el transpilador inverso de Mojo."""

from cobra.transpilers.reverse.from_mojo import ReverseFromMojo
from core.ast_nodes import NodoAsignacion, NodoIdentificador, NodoValor


def test_reverse_from_mojo_assignment():
    code = "let y = 3.14"
    ast = ReverseFromMojo().generate_ast(code)
    assert len(ast) == 1
    nodo = ast[0]
    assert isinstance(nodo, NodoAsignacion)
    assert isinstance(nodo.variable, NodoIdentificador)
    assert nodo.variable.nombre == "y"
    assert isinstance(nodo.expresion, NodoValor)
    assert abs(nodo.expresion.valor - 3.14) < 1e-6

