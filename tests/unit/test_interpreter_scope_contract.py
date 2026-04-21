from __future__ import annotations

from io import StringIO
from unittest.mock import patch

import pytest

from cobra.core import Token, TipoToken
from core.ast_nodes import (
    NodoAsignacion,
    NodoBucleMientras,
    NodoFuncion,
    NodoIdentificador,
    NodoLlamadaFuncion,
    NodoOperacionBinaria,
    NodoRetorno,
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


def test_shadowing_define_local_y_set_al_scope_mas_cercano() -> None:
    with patch.object(
        InterpretadorCobra,
        "_asegurar_no_autorreferencia_asignacion",
        return_value=None,
    ):
        inter = _ejecutar(
            [
                NodoAsignacion("x", NodoValor(100), declaracion=True),
                NodoFuncion(
                    "wrapper",
                    [],
                    [
                        NodoAsignacion("x", NodoValor(1), declaracion=True),
                        NodoFuncion(
                            "tocar_local",
                            [],
                            [
                                NodoAsignacion(
                                    "x",
                                    NodoOperacionBinaria(
                                        NodoIdentificador("x"),
                                        Token(TipoToken.SUMA, "+"),
                                        NodoValor(1),
                                    ),
                                )
                            ],
                        ),
                        NodoLlamadaFuncion("tocar_local", []),
                    ],
                ),
                NodoLlamadaFuncion("wrapper", []),
            ]
        )

    assert inter.obtener_variable("x") == 100


def test_closure_usa_environment_parent_en_llamadas() -> None:
    with patch.object(
        InterpretadorCobra,
        "_asegurar_no_autorreferencia_asignacion",
        return_value=None,
    ):
        inter = _ejecutar(
            [
                NodoAsignacion("base", NodoValor(10), declaracion=True),
                NodoFuncion(
                    "externa",
                    [],
                    [
                        NodoAsignacion("x", NodoValor(5), declaracion=True),
                        NodoFuncion(
                            "interna",
                            [],
                            [
                                NodoRetorno(
                                    NodoIdentificador("x")
                                )
                            ],
                        ),
                        NodoRetorno(NodoLlamadaFuncion("interna", [])),
                    ],
                ),
                NodoAsignacion(
                    "resultado",
                    NodoLlamadaFuncion("externa", []),
                    declaracion=True,
                ),
            ]
        )

    assert inter.obtener_variable("resultado") == 5


def test_contrato_anticoopia_entorno_cierre_observa_mutaciones_posteriores() -> None:
    with patch.object(
        InterpretadorCobra,
        "_asegurar_no_autorreferencia_asignacion",
        return_value=None,
    ):
        inter = _ejecutar(
            [
                NodoAsignacion("x", NodoValor(1), declaracion=True),
                NodoFuncion(
                    "leer_x",
                    [],
                    [NodoRetorno(NodoIdentificador("x"))],
                ),
                NodoAsignacion("x", NodoValor(2)),
                NodoAsignacion(
                    "resultado",
                    NodoLlamadaFuncion("leer_x", []),
                    declaracion=True,
                ),
            ]
        )

    funcion = inter.obtener_variable("leer_x")
    assert funcion["entorno"] is inter.contextos[0]
    assert inter.obtener_variable("resultado") == 2


def test_asignar_sin_declarar_falla_con_name_error() -> None:
    with pytest.raises(NameError, match=r"^Variable no declarada: x$"):
        _ejecutar([NodoAsignacion("x", NodoValor(10))])
