"""Pruebas para el transpilador inverso de ensamblador."""

from cobra.transpilers.reverse.from_asm import ReverseFromASM
from core.ast_nodes import NodoAsignacion, NodoIdentificador, NodoValor


def test_reverse_from_asm_mov():
    code = "MOV R1, 5"
    ast = ReverseFromASM().generate_ast(code)
    assert len(ast) == 1
    nodo = ast[0]
    assert isinstance(nodo, NodoAsignacion)
    assert isinstance(nodo.variable, NodoIdentificador)
    assert nodo.variable.nombre == "R1"
    assert isinstance(nodo.expresion, NodoValor)
    assert nodo.expresion.valor == 5

