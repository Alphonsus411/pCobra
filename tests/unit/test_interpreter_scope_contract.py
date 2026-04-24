from __future__ import annotations

import inspect
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
from pcobra.core.environment import Environment


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


def test_mientras_reasigna_memoria_en_entorno_real_y_persiste_fuera() -> None:
    inter = InterpretadorCobra()
    inter.ejecutar_asignacion(NodoAsignacion("i", NodoValor(0), declaracion=True))
    inter.mem_contextos[0]["i"] = (11, 1)

    liberaciones: list[tuple[int, int]] = []
    solicitudes = iter([22, 33])
    inter.liberar_memoria = lambda idx, tam: liberaciones.append((idx, tam))
    inter.solicitar_memoria = lambda tam: next(solicitudes)

    condicion = NodoOperacionBinaria(
        NodoIdentificador("i"),
        Token(TipoToken.MENORQUE, "<"),
        NodoValor(2),
    )
    incremento = NodoAsignacion(
        "i",
        NodoOperacionBinaria(
            NodoIdentificador("i"),
            Token(TipoToken.SUMA, "+"),
            NodoValor(1),
        ),
    )

    with patch.object(
        InterpretadorCobra,
        "_asegurar_no_autorreferencia_asignacion",
        return_value=None,
    ):
        inter.ejecutar_mientras(NodoBucleMientras(condicion, [incremento]))

    assert inter.obtener_variable("i") == 2
    assert liberaciones == [(11, 1), (22, 1)]
    assert inter.mem_contextos[0]["i"] == (33, 1)



def test_closure_mutacion_reasigna_en_padre_y_persiste_tras_salir() -> None:
    inter = InterpretadorCobra()
    inter.ejecutar_asignacion(NodoAsignacion("base", NodoValor(10), declaracion=True))
    inter.mem_contextos[0]["base"] = (100, 1)

    liberaciones: list[tuple[int, int]] = []
    inter.liberar_memoria = lambda idx, tam: liberaciones.append((idx, tam))
    inter.solicitar_memoria = lambda tam: 200

    closure = NodoFuncion(
        "sumar_uno",
        [],
        [
            NodoAsignacion(
                "base",
                NodoOperacionBinaria(
                    NodoIdentificador("base"),
                    Token(TipoToken.SUMA, "+"),
                    NodoValor(1),
                ),
            )
        ],
    )

    with patch.object(
        InterpretadorCobra,
        "_asegurar_no_autorreferencia_asignacion",
        return_value=None,
    ):
        inter.ejecutar_funcion(closure)
        inter.ejecutar_llamada_funcion(NodoLlamadaFuncion("sumar_uno", []))

    assert inter.obtener_variable("base") == 11
    assert liberaciones == [(100, 1)]
    assert inter.mem_contextos[0]["base"] == (200, 1)
    assert len(inter.contextos) == 1
    assert len(inter.mem_contextos) == 1


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
                        NodoRetorno(NodoIdentificador("x")),
                    ],
                ),
                NodoAsignacion(
                    "resultado_local",
                    NodoLlamadaFuncion("wrapper", []),
                    declaracion=True,
                ),
            ]
        )

    assert inter.obtener_variable("x") == 100
    assert inter.obtener_variable("resultado_local") == 1


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


def test_environment_set_no_copia_entorno_usa_referencias_vivas() -> None:
    global_env = Environment(values={"x": 1})
    hijo = Environment(parent=global_env)
    nieto = Environment(parent=hijo)

    hijo.set("x", 2)
    assert global_env.values["x"] == 2

    alias_values = global_env.values
    nieto.set("x", 3)
    assert global_env.values is alias_values
    assert alias_values["x"] == 3
    assert hijo.parent is global_env
    assert nieto.parent is hijo


def test_environment_set_prioriza_scope_mas_cercano_en_reasignacion_cruzada() -> None:
    global_env = Environment(values={"x": 1})
    intermedio = Environment(values={"x": 2}, parent=global_env)
    interno = Environment(parent=intermedio)

    interno.set("x", 9)

    assert intermedio.values["x"] == 9
    assert global_env.values["x"] == 1


def test_environment_scope_sin_copy_ni_clonado_dict_en_define_set() -> None:
    codigo_define = inspect.getsource(Environment.define)
    codigo_set = inspect.getsource(Environment.set)
    codigo_contains = inspect.getsource(Environment.contains)
    agregado = f"{codigo_define}\n{codigo_set}\n{codigo_contains}".lower()

    assert ".copy(" not in agregado
    assert "dict(" not in agregado


def test_reset_context_values_reemplaza_scope_activo_sin_romper_parent() -> None:
    inter = InterpretadorCobra()
    global_env = inter.contextos[0]
    global_env.define("g", 1)
    inter.contextos.append(Environment(parent=global_env, values={"x": 10}))
    inter.mem_contextos.append({})
    try:
        inter.reset_context_values({"x": 99, "y": 7})

        assert inter.contextos[-1].values == {"x": 99, "y": 7}
        assert global_env.values == {"g": 1}
        assert inter.contextos[-1].parent is global_env
    finally:
        inter.mem_contextos.pop()
        inter.contextos.pop()


def test_contexto_repl_consistente_tras_multiples_ejecuciones() -> None:
    inter = InterpretadorCobra()
    with patch.object(
        InterpretadorCobra,
        "_asegurar_no_autorreferencia_asignacion",
        return_value=None,
    ):
        inter.ejecutar_nodo(NodoAsignacion("x", NodoValor(1), declaracion=True))
        inter.ejecutar_nodo(
            NodoAsignacion(
                "x",
                NodoOperacionBinaria(
                    NodoIdentificador("x"),
                    Token(TipoToken.SUMA, "+"),
                    NodoValor(4),
                ),
            )
        )
        inter.ejecutar_nodo(
            NodoAsignacion(
                "z",
                NodoOperacionBinaria(
                    NodoIdentificador("x"),
                    Token(TipoToken.SUMA, "+"),
                    NodoValor(1),
                ),
                declaracion=True,
            )
        )

    assert inter.obtener_variable("x") == 5
    assert inter.obtener_variable("z") == 6
    assert len(inter.contextos) == 1
    assert len(inter.mem_contextos) == 1
    assert inter.contextos[0].parent is None


def test_interpreter_control_flow_sin_copy_ni_clonado_en_bloques_y_bucles() -> None:
    codigo_mientras = inspect.getsource(InterpretadorCobra.ejecutar_mientras).lower()
    codigo_condicional = inspect.getsource(InterpretadorCobra.ejecutar_condicional).lower()
    agregado = f"{codigo_mientras}\n{codigo_condicional}"

    assert "copy(" not in agregado
    assert "deepcopy(" not in agregado
