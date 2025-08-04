"""Pruebas para el transpilador inverso de COBOL."""

from cobra.transpilers.reverse.from_cobol import ReverseFromCOBOL
from core.ast_nodes import NodoAsignacion, NodoIdentificador, NodoValor


def test_reverse_from_cobol_move():
    code = "MOVE 7 TO RESULT."
    ast = ReverseFromCOBOL().generate_ast(code)
    assert len(ast) == 1
    nodo = ast[0]
    assert isinstance(nodo, NodoAsignacion)
    assert isinstance(nodo.variable, NodoIdentificador)
    assert nodo.variable.nombre == "RESULT"
    assert isinstance(nodo.expresion, NodoValor)
    assert nodo.expresion.valor == 7

