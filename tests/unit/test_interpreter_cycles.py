import pytest

from core.interpreter import InterpretadorCobra
from core.ast_nodes import NodoIdentificador, NodoValor


def test_referencia_circular_variable():
    inter = InterpretadorCobra()
    inter.variables["a"] = NodoIdentificador("b")
    inter.variables["b"] = NodoIdentificador("a")
    with pytest.raises(RuntimeError, match="Referencia circular"):
        inter.evaluar_expresion(NodoIdentificador("a"))


def test_resolucion_encadenada_sin_ciclo():
    inter = InterpretadorCobra()
    inter.variables["a"] = NodoIdentificador("b")
    inter.variables["b"] = NodoValor(3)
    assert inter.evaluar_expresion(NodoIdentificador("a")) == 3
