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


def test_metodo_definido_en_base_se_ejecuta_desde_subclase():
    inter = InterpretadorCobra()

    metodo_base = NodoMetodo("saludo", ["self"], [NodoRetorno(NodoValor("hola"))])
    clase_base = NodoClase("Base", [metodo_base])
    inter.ejecutar_clase(clase_base)

    clase_derivada = NodoClase("Derivada", [], bases=["Base"])
    inter.ejecutar_clase(clase_derivada)

    inter.ejecutar_nodo(NodoAsignacion("obj", NodoInstancia("Derivada")))

    resultado = inter.evaluar_expresion(
        NodoLlamadaMetodo(NodoIdentificador("obj"), "saludo", [])
    )

    assert resultado == "hola"

