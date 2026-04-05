from __future__ import annotations

from io import StringIO
from unittest.mock import patch

import pytest

from cobra.core import Lexer, Parser
from core.interpreter import InterpretadorCobra


def _parsear_y_ejecutar(codigo: str) -> str:
    """Parsea y ejecuta código Cobra, separando incidencia de parser/evaluador."""
    try:
        tokens = Lexer(codigo).analizar_token()
        ast = Parser(tokens).parsear()
    except Exception as exc:  # pragma: no cover - contrato explícito
        pytest.fail(f"Error de parseo/sintaxis inesperado: {exc}")

    try:
        with patch("sys.stdout", new_callable=StringIO) as out:
            InterpretadorCobra().ejecutar_ast(ast)
    except Exception as exc:  # pragma: no cover - contrato explícito
        pytest.fail(
            "Incidencia separada del evaluador: parseo correcto, "
            f"pero falló la evaluación con: {exc}"
        )

    lineas = [linea.strip() for linea in out.getvalue().splitlines() if linea.strip()]
    return lineas[-1] if lineas else ""


def test_igualdad_cadenas_hola_hola_es_verdadero() -> None:
    salida = _parsear_y_ejecutar('imprimir "hola" == "hola"\n')
    assert salida == "verdadero"


def test_igualdad_cadenas_hola_adios_es_falso() -> None:
    salida = _parsear_y_ejecutar('imprimir "hola" == "adios"\n')
    assert salida == "falso"
