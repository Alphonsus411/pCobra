from __future__ import annotations

import pytest

from pcobra.core.ast_nodes import (
    NodoAsignacion,
    NodoAtributo,
    NodoClase,
    NodoFuncion,
    NodoIdentificador,
    NodoInstancia,
    NodoLista,
    NodoLlamadaFuncion,
    NodoOperacionBinaria,
    NodoRetorno,
    NodoValor,
)
from pcobra.core.interpreter import InterpretadorCobra
from pcobra.core.lexer import TipoToken, Token


def test_primera_asignacion_superior_de_numero() -> None:
    inter = InterpretadorCobra()

    assert inter.ejecutar_nodo(NodoAsignacion("numero", NodoValor(7))) == 7
    assert inter.obtener_variable("numero") == 7


def test_primera_asignacion_superior_de_cadena() -> None:
    inter = InterpretadorCobra()

    assert inter.ejecutar_nodo(NodoAsignacion("texto", NodoValor("cobra"))) == "cobra"
    assert inter.obtener_variable("texto") == "cobra"


def test_primera_asignacion_superior_de_lista() -> None:
    inter = InterpretadorCobra()

    lista = NodoLista([NodoValor(1), NodoValor(2)])

    assert inter.ejecutar_nodo(NodoAsignacion("valores", lista)) == [1, 2]
    assert inter.obtener_variable("valores") == [1, 2]


def test_primera_asignacion_superior_de_operacion_aritmetica() -> None:
    inter = InterpretadorCobra()
    suma = NodoOperacionBinaria(
        NodoValor(2),
        Token(TipoToken.SUMA, "+"),
        NodoValor(3),
    )

    assert inter.ejecutar_nodo(NodoAsignacion("total", suma)) == 5
    assert inter.obtener_variable("total") == 5


def test_primera_asignacion_superior_de_instancia() -> None:
    inter = InterpretadorCobra()
    inter.ejecutar_nodo(NodoClase("Vacia", []))

    instancia = inter.ejecutar_nodo(NodoAsignacion("objeto", NodoInstancia("Vacia")))

    assert inter.obtener_variable("objeto") is instancia
    assert instancia["__clase__"]["nombre"] == "Vacia"


def test_declaracion_explicita_define_binding() -> None:
    inter = InterpretadorCobra()

    inter.ejecutar_nodo(NodoAsignacion("declarada", NodoValor(11), declaracion=True))

    assert inter.obtener_variable("declarada") == 11


def test_inferencia_define_binding() -> None:
    inter = InterpretadorCobra()

    inter.ejecutar_nodo(NodoAsignacion("inferida", NodoValor(13), inferencia=True))

    assert inter.obtener_variable("inferida") == 13


def test_primera_asignacion_local_de_funcion_define_binding_local() -> None:
    inter = InterpretadorCobra()
    inter.ejecutar_nodo(
        NodoFuncion(
            "crear_local",
            [],
            [
                NodoAsignacion("local", NodoValor(17)),
                NodoRetorno(NodoIdentificador("local")),
            ],
        )
    )

    assert inter.ejecutar_nodo(NodoLlamadaFuncion("crear_local", [])) == 17
    with pytest.raises(NameError, match=r"^Variable no declarada: local$"):
        inter.obtener_variable("local")


def test_mutacion_posterior_actualiza_binding_existente() -> None:
    inter = InterpretadorCobra()
    inter.ejecutar_nodo(NodoAsignacion("contador", NodoValor(1)))

    inter.ejecutar_nodo(NodoAsignacion("contador", NodoValor(2)))

    assert inter.obtener_variable("contador") == 2


def test_asignacion_de_atributo_actualiza_instancia_existente() -> None:
    inter = InterpretadorCobra()
    inter.ejecutar_nodo(NodoClase("Caja", []))
    inter.ejecutar_nodo(NodoAsignacion("caja", NodoInstancia("Caja")))

    inter.ejecutar_nodo(
        NodoAsignacion(
            NodoAtributo(NodoIdentificador("caja"), "valor"),
            NodoValor(19),
        )
    )

    caja = inter.obtener_variable("caja")
    assert caja["__atributos__"]["valor"] == 19


def test_nodo_atributo_exige_binding_previo() -> None:
    inter = InterpretadorCobra()
    asignacion = NodoAsignacion(
        NodoAtributo(NodoIdentificador("ausente"), "valor"),
        NodoValor(23),
    )

    with pytest.raises(NameError, match=r"^Variable no declarada: ausente$"):
        inter.ejecutar_nodo(asignacion)
