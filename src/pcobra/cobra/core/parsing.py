"""Frontera neutral entre el Parser sintáctico y consumidores semánticos."""

from __future__ import annotations

import os
from typing import Any, Iterable

from pcobra.cobra.core.lexer import Lexer
from pcobra.cobra.core.parser import Parser
from pcobra.cobra.core.resolucion_instancias import resolver_instanciaciones


def parsear_tokens_resuelto(
    tokens: Iterable[Any],
    *,
    parser_cls: type[Any] = Parser,
    parsear_kwargs: dict[str, Any] | None = None,
) -> list[Any]:
    """Parsea tokens y aplica la resolución neutral posterior al Parser."""

    return resolver_instanciaciones(
        parser_cls(list(tokens)).parsear(**(parsear_kwargs or {}))
    )


def parsear_codigo_resuelto(codigo: str, *, usar_cache: bool = True) -> list[Any]:
    """Devuelve el AST público resuelto, usando la caché sólo si está configurada.

    La ausencia de ``SQLITE_DB_KEY`` es una configuración normal: en ese caso
    se ejecutan Lexer y Parser directamente. Si la caché está configurada, sus
    errores no se ocultan y continúan propagándose al llamador.
    """

    sqlite_db_key = os.environ.get("SQLITE_DB_KEY")
    cache_configurada = bool(sqlite_db_key and sqlite_db_key.strip())
    if usar_cache and cache_configurada:
        from pcobra.core.ast_cache import obtener_ast

        return obtener_ast(codigo)

    return parsear_tokens_resuelto(Lexer(codigo).tokenizar())
