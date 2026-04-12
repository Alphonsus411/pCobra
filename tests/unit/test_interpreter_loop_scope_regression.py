from __future__ import annotations

from io import StringIO
from unittest.mock import patch

import pytest

from cobra.core import Lexer, Parser
from core.interpreter import InterpretadorCobra


def _ejecutar_codigo_y_capturar_stdout(codigo: str) -> str:
    tokens = Lexer(codigo).tokenizar()
    ast = Parser(tokens).parsear()
    inter = InterpretadorCobra()

    with patch("sys.stdout", new_callable=StringIO) as out:
        with patch.object(
            InterpretadorCobra,
            "_asegurar_no_autorreferencia_asignacion",
            return_value=None,
        ):
            for nodo in ast:
                inter.ejecutar_nodo(nodo)

    return out.getvalue()


def _lineas_sin_trazas(salida: str) -> list[str]:
    return [
        linea.strip()
        for linea in salida.splitlines()
        if linea.strip() and not linea.lstrip().startswith("[")
    ]


def test_mientras_reutiliza_variable_externa_sin_crear_scope() -> None:
    codigo = """
var i = 10
mientras i < 12:
    i = i + 1
fin
imprimir(i)
"""

    try:
        salida = _ejecutar_codigo_y_capturar_stdout(codigo)
    except NameError as exc:  # pragma: no cover - regresión explícita
        pytest.fail(f"No debía lanzar NameError: {exc}")

    lineas = _lineas_sin_trazas(salida)
    assert lineas[-1] == "12"
    assert "NameError: Variable no declarada: i" not in salida


def test_si_reutiliza_variable_externa_sin_crear_scope() -> None:
    codigo = """
var i = 10
si verdadero:
    i = i + 2
fin
imprimir(i)
"""

    try:
        salida = _ejecutar_codigo_y_capturar_stdout(codigo)
    except NameError as exc:  # pragma: no cover - regresión explícita
        pytest.fail(f"No debía lanzar NameError: {exc}")

    lineas = _lineas_sin_trazas(salida)
    assert lineas[-1] == "12"
    assert "NameError: Variable no declarada: i" not in salida
