import pytest

from core.interpreter import InterpretadorCobra
from core.ast_nodes import NodoAsignacion, NodoIdentificador, NodoValor


def test_referencia_circular_variable():
    inter = InterpretadorCobra()
    inter.variables["a"] = NodoIdentificador("b")
    inter.variables["b"] = NodoIdentificador("a")
    with pytest.raises(RuntimeError, match="Ciclo de variables detectado"):
        inter.evaluar_expresion(NodoIdentificador("a"))


def test_resolucion_encadenada_sin_ciclo():
    inter = InterpretadorCobra()
    inter.variables["a"] = NodoIdentificador("b")
    inter.variables["b"] = NodoValor(3)
    assert inter.evaluar_expresion(NodoIdentificador("a")) == 3


def test_name_error_variable_ausente_se_distingue_de_ciclo():
    inter = InterpretadorCobra()
    with pytest.raises(NameError, match=r"^Variable no declarada: z$"):
        inter.evaluar_expresion(NodoIdentificador("z"))


def test_variable_apuntando_a_asignacion_autorreferente():
    inter = InterpretadorCobra()
    inter.variables["a"] = NodoAsignacion("tmp", NodoIdentificador("a"))
    with pytest.raises(
        RuntimeError, match=r"^Asignación circular inválida para variable 'a'$"
    ):
        inter.evaluar_expresion(NodoIdentificador("a"))
