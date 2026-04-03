from __future__ import annotations

from io import StringIO
from unittest.mock import patch

import pytest

from cobra.core import Lexer, Parser, TipoToken, Token
from core.ast_nodes import (
    NodoAsignacion,
    NodoCondicional,
    NodoIdentificador,
    NodoImprimir,
    NodoOperacionBinaria,
    NodoValor,
)
from core.interpreter import InterpretadorCobra


def _ejecutar_codigo(codigo: str) -> InterpretadorCobra:
    tokens = Lexer(codigo).tokenizar()
    ast = Parser(tokens).parsear()
    inter = InterpretadorCobra()
    for nodo in ast:
        inter.ejecutar_nodo(nodo)
    return inter


def test_condicional_valido_con_variable_definida() -> None:
    inter = _ejecutar_codigo(
        """
var x = 1
si x == 1:
    var z = 99
fin
"""
    )
    assert inter.variables["z"] == 99


def test_condicional_con_variable_no_definida_lanza_nameerror() -> None:
    with pytest.raises(NameError, match=r"^Variable no declarada: y$"):
        _ejecutar_codigo(
            """
si y == 1:
    pasar
fin
"""
        )


def test_condicionales_anidados_se_ejecutan_correctamente() -> None:
    inter = _ejecutar_codigo(
        """
var bandera = 1
si bandera == 1:
    si 2 > 1:
        var valor = 7
    sino:
        var valor = 0
    fin
fin
"""
    )
    assert inter.variables["valor"] == 7


def test_anidamiento_profundo_no_lanza_recursion_error() -> None:
    profundidad = 8
    codigo = ["var ok = 0"]
    codigo.extend("    " * i + "si 1 == 1:" for i in range(profundidad))
    codigo.append("    " * profundidad + "var ok = 1")
    codigo.extend("    " * i + "fin" for i in reversed(range(profundidad)))

    try:
        inter = _ejecutar_codigo("\n".join(codigo))
    except RecursionError as exc:  # pragma: no cover - contrato explícito
        pytest.fail(f"No debía lanzar RecursionError: {exc}")

    assert inter.variables["ok"] == 1


def test_identificador_y_en_declaracion_y_uso() -> None:
    inter = _ejecutar_codigo(
        """
var y = 3
var resultado = y + 4
"""
    )
    assert inter.variables["resultado"] == 7


def test_ast_imprimir_comparacion_booleana_sin_recursionerror() -> None:
    inter = InterpretadorCobra()
    ast = [
        NodoAsignacion("x", NodoValor(10)),
        NodoImprimir(
            NodoOperacionBinaria(
                NodoIdentificador("x"),
                Token(TipoToken.IGUAL, "=="),
                NodoValor(10),
            )
        ),
    ]

    try:
        with patch("sys.stdout", new_callable=StringIO) as out:
            for nodo in ast:
                inter.ejecutar_nodo(nodo)
    except RecursionError as exc:
        pytest.fail(f"No debía lanzar RecursionError: {exc}")

    assert out.getvalue().strip() in {"True", "False"}


def test_ast_condicional_ejecuta_bloque_sin_recursionerror() -> None:
    inter = InterpretadorCobra()
    ast = [
        NodoAsignacion("x", NodoValor(10)),
        NodoCondicional(
            NodoOperacionBinaria(
                NodoIdentificador("x"),
                Token(TipoToken.IGUAL, "=="),
                NodoValor(10),
            ),
            [NodoImprimir(NodoValor("ok"))],
            [],
        ),
    ]

    try:
        with patch("sys.stdout", new_callable=StringIO) as out:
            for nodo in ast:
                inter.ejecutar_nodo(nodo)
    except RecursionError as exc:
        pytest.fail(f"No debía lanzar RecursionError: {exc}")

    assert out.getvalue().strip() == "ok"


def test_ast_comparacion_identificador_indefinido_controla_nameerror_sin_recursionerror() -> None:
    inter = InterpretadorCobra()
    nodo = NodoImprimir(
        NodoOperacionBinaria(
            NodoIdentificador("y"),
            Token(TipoToken.IGUAL, "=="),
            NodoValor(10),
        )
    )

    try:
        with patch("sys.stdout", new_callable=StringIO) as out:
            inter.ejecutar_nodo(nodo)
    except RecursionError as exc:
        pytest.fail(f"No debía lanzar RecursionError: {exc}")

    assert out.getvalue().strip() == "Variable no declarada: y"
