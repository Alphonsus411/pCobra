"""Pipeline compartido de análisis/ejecución para CLI Cobra."""

from __future__ import annotations

from typing import Any

from pcobra.cobra.core import Lexer, Parser


def analizar_codigo(codigo: str) -> Any:
    """Analiza código fuente con el pipeline canónico Lexer+Parser."""

    tokens = Lexer(codigo).tokenizar()
    return Parser(tokens).parsear()


def ejecutar_ast(ast: Any, interpreter: Any) -> Any:
    """Ejecuta un AST usando una instancia explícita de intérprete."""

    return interpreter.ejecutar_ast(ast)
