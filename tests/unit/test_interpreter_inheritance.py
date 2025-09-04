import pytest
from core.interpreter import InterpretadorCobra
from core.ast_nodes import (
    NodoClase,
    NodoMetodo,
    NodoRetorno,
    NodoValor,
    NodoInstancia,
    NodoAsignacion,
    NodoLlamadaMetodo,
    NodoIdentificador,
)


def test_metodo_en_segunda_base():
    inter = InterpretadorCobra()
    clase_a = NodoClase("A", [])
    metodo_b = NodoMetodo("saludo", ["self"], [NodoRetorno(NodoValor("desde B"))])
    clase_b = NodoClase("B", [metodo_b])
    inter.ejecutar_clase(clase_a)
    inter.ejecutar_clase(clase_b)
    clase_c = NodoClase("C", [], bases=["A", "B"])
    inter.ejecutar_clase(clase_c)
    inter.ejecutar_nodo(NodoAsignacion("obj", NodoInstancia("C")))
    resultado = inter.evaluar_expresion(
        NodoLlamadaMetodo(NodoIdentificador("obj"), "saludo", [])
    )
    assert resultado == "desde B"


def test_metodo_no_encontrado_en_bases():
    inter = InterpretadorCobra()
    clase_a = NodoClase("A", [])
    clase_b = NodoClase("B", [])
    inter.ejecutar_clase(clase_a)
    inter.ejecutar_clase(clase_b)
    clase_d = NodoClase("D", [], bases=["A", "B"])
    inter.ejecutar_clase(clase_d)
    inter.ejecutar_nodo(NodoAsignacion("obj", NodoInstancia("D")))
    with pytest.raises(ValueError, match="no encontrado"):
        inter.evaluar_expresion(
            NodoLlamadaMetodo(NodoIdentificador("obj"), "saludo", [])
        )
