import pytest

from core.interpreter import InterpretadorCobra
from core.ast_nodes import (
    NodoAsignacion,
    NodoBloque,
    NodoCondicional,
    NodoIdentificador,
    NodoValor,
)


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


def test_ejecutar_asignacion_rechaza_autorreferencia_directa():
    inter = InterpretadorCobra()
    with pytest.raises(
        RuntimeError, match=r"^Asignación circular inválida para variable 'a'$"
    ):
        inter.ejecutar_asignacion(NodoAsignacion("a", NodoIdentificador("a")))


def test_ejecutar_asignacion_rechaza_autorreferencia_indirecta():
    inter = InterpretadorCobra()
    inter.variables["b"] = NodoIdentificador("a")
    with pytest.raises(RuntimeError, match=r"^Ciclo de variables detectado en 'a'$"):
        inter.ejecutar_asignacion(NodoAsignacion("a", NodoIdentificador("b")))


def test_condicional_rechaza_nodo_ast_sin_materializar_en_condicion():
    inter = InterpretadorCobra()
    condicional = NodoCondicional(
        condicion=NodoValor(NodoIdentificador("x")),
        bloque_si=NodoBloque([]),
        bloque_sino=NodoBloque([]),
    )

    with pytest.raises(
        RuntimeError,
        match=r"^Condición no materializada: se recibió nodo AST NodoIdentificador$",
    ):
        inter.ejecutar_condicional(condicional)
