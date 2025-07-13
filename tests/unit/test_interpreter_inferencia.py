from core.interpreter import InterpretadorCobra
from core.ast_nodes import NodoAsignacion, NodoValor


def test_interpreter_variable_inferencia():
    inter = InterpretadorCobra()
    nodo = NodoAsignacion("x", NodoValor(7), True)
    inter.ejecutar_asignacion(nodo)
    assert inter.variables["x"] == 7
