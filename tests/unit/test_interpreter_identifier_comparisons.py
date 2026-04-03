from __future__ import annotations

from io import StringIO
from unittest.mock import patch

import pytest

from cobra.core import TipoToken, Token
from core.ast_nodes import (
    NodoAsignacion,
    NodoCondicional,
    NodoIdentificador,
    NodoImprimir,
    NodoOperacionBinaria,
    NodoValor,
)
from core.interpreter import InterpretadorCobra
from core.lexer import Lexer
from core.parser import Parser


def _ejecutar_codigo_y_capturar_salida(codigo: str) -> str:
    tokens = Lexer(codigo).tokenizar()
    ast = Parser(tokens).parsear()
    inter = InterpretadorCobra()

    try:
        with patch("sys.stdout", new_callable=StringIO) as out:
            for nodo in ast:
                inter.ejecutar_nodo(nodo)
    except RecursionError as exc:  # pragma: no cover - contrato explícito
        pytest.fail(f"No debía lanzar RecursionError: {exc}")

    return out.getvalue().strip()


def test_comparacion_identificador_en_imprimir_sin_recursionerror() -> None:
    salida = _ejecutar_codigo_y_capturar_salida(
        """
x = 10
imprimir x == 10
"""
    )
    assert salida == "True"


def test_comparacion_identificador_en_condicional_sin_recursionerror() -> None:
    salida = _ejecutar_codigo_y_capturar_salida(
        """
x = 10
si x == 10:
    imprimir "ok"
fin
"""
    )
    assert salida == "ok"


def test_identificador_indefinido_en_comparacion_controlado_sin_recursionerror() -> None:
    codigo = 'imprimir y == 10\n'

    try:
        salida = _ejecutar_codigo_y_capturar_salida(codigo)
    except NameError as exc:
        assert "Variable no declarada: y" in str(exc)
        return
    except RecursionError as exc:  # pragma: no cover - contrato explícito
        pytest.fail(f"No debía lanzar RecursionError: {exc}")

    assert salida == "Variable no declarada: y"


def test_ast_directo_comparacion_identificador_sin_recursionerror() -> None:
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
    except RecursionError as exc:  # pragma: no cover - contrato explícito
        pytest.fail(f"No debía lanzar RecursionError: {exc}")

    assert out.getvalue().strip() == "True"


def test_ast_directo_condicional_identificador_sin_recursionerror() -> None:
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
    except RecursionError as exc:  # pragma: no cover - contrato explícito
        pytest.fail(f"No debía lanzar RecursionError: {exc}")

    assert out.getvalue().strip() == "ok"
