from __future__ import annotations

import pytest
from unittest.mock import patch

from cobra.core import Token, TipoToken
from core.ast_nodes import (
    NodoAsignacion,
    NodoBucleMientras,
    NodoFuncion,
    NodoIdentificador,
    NodoLlamadaFuncion,
    NodoOperacionBinaria,
    NodoValor,
)
from core.interpreter import InterpretadorCobra


def _ejecutar(nodos: list) -> InterpretadorCobra:
    inter = InterpretadorCobra()
    for nodo in nodos:
        inter.ejecutar_nodo(nodo)
    return inter


def test_reasignacion_en_mientras_persiste_fuera_del_loop() -> None:
    inter = InterpretadorCobra()
    inter.ejecutar_asignacion(NodoAsignacion("i", NodoValor(0), declaracion=True))
    condicion = NodoOperacionBinaria(
        NodoIdentificador("i"),
        Token(TipoToken.MENORQUE, "<"),
        NodoValor(3),
    )
    incremento = NodoAsignacion(
        "i",
        NodoOperacionBinaria(
            NodoIdentificador("i"),
            Token(TipoToken.SUMA, "+"),
            NodoValor(1),
        ),
    )
    bucle = NodoBucleMientras(condicion, [incremento])
    with patch.object(
        InterpretadorCobra,
        "_asegurar_no_autorreferencia_asignacion",
        return_value=None,
    ):
        inter.ejecutar_mientras(bucle)

    assert inter.obtener_variable("i") == 3


def test_reasignacion_en_funcion_actualiza_scope_capturado_padre() -> None:
    with patch.object(
        InterpretadorCobra,
        "_asegurar_no_autorreferencia_asignacion",
        return_value=None,
    ):
        inter = _ejecutar(
            [
                NodoAsignacion("contador", NodoValor(0), declaracion=True),
                NodoFuncion(
                    "subir",
                    [],
                    [
                        NodoAsignacion(
                            "contador",
                            NodoOperacionBinaria(
                                NodoIdentificador("contador"),
                                Token(TipoToken.SUMA, "+"),
                                NodoValor(1),
                            ),
                        )
                    ],
                ),
                NodoLlamadaFuncion("subir", []),
            ]
        )

    assert inter.obtener_variable("contador") == 1


def test_asignar_sin_declarar_falla_con_name_error() -> None:
    with pytest.raises(NameError, match=r"^Variable no declarada: x$"):
        _ejecutar([NodoAsignacion("x", NodoValor(10))])
