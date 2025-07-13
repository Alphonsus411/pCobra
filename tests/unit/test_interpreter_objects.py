from core.interpreter import InterpretadorCobra
from core.ast_nodes import (
    NodoClase,
    NodoMetodo,
    NodoInstancia,
    NodoAsignacion,
    NodoLlamadaMetodo,
    NodoAtributo,
    NodoIdentificador,
    NodoValor,
    NodoRetorno,
)



def test_creacion_instancia_y_metodo():
    inter = InterpretadorCobra()

    metodo = NodoMetodo("saludar", ["self"], [NodoRetorno(NodoValor("hola"))])
    clase = NodoClase("Persona", [metodo])
    inter.ejecutar_nodo(clase)

    inter.ejecutar_nodo(NodoAsignacion("p", NodoInstancia("Persona")))
    res = inter.ejecutar_nodo(
        NodoLlamadaMetodo(NodoIdentificador("p"), "saludar", [])
    )
    assert res == "hola"


def test_atributos_en_instancia():
    inter = InterpretadorCobra()

    set_nombre = NodoMetodo(
        "set_nombre",
        ["self", "nombre"],
        [
            NodoAsignacion(
                NodoAtributo(NodoIdentificador("self"), "nombre"),
                NodoIdentificador("nombre"),
            )
        ],
    )
    get_nombre = NodoMetodo(
        "get_nombre",
        ["self"],
        [NodoRetorno(NodoAtributo(NodoIdentificador("self"), "nombre"))],
    )
    clase = NodoClase("Persona", [set_nombre, get_nombre])
    inter.ejecutar_nodo(clase)

    inter.ejecutar_nodo(NodoAsignacion("p", NodoInstancia("Persona")))
    inter.ejecutar_nodo(
        NodoLlamadaMetodo(NodoIdentificador("p"), "set_nombre", [NodoValor("Ana")])
    )
    nombre = inter.ejecutar_nodo(
        NodoLlamadaMetodo(NodoIdentificador("p"), "get_nombre", [])
    )
    assert nombre == "Ana"
