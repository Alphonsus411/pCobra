"""Funciones auxiliares para manejar autocompletado opcional en la CLI."""
from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)

try:  # pragma: no cover - depende de una librería externa opcional
    import argcomplete  # type: ignore
    from argcomplete.completers import (  # type: ignore
        DirectoriesCompleter as _DirectoriesCompleter,
        FilesCompleter as _FilesCompleter,
    )
except ModuleNotFoundError:  # pragma: no cover - entornos sin argcomplete
    argcomplete = None  # type: ignore[assignment]
    _FilesCompleter = None  # type: ignore[assignment]
    _DirectoriesCompleter = None  # type: ignore[assignment]
    logger.debug(
        "argcomplete no está instalado; las funciones de autocompletado se desactivarán.",
    )


class _NoOpCompleter:
    """Objeto nulo que imita la interfaz de un completer de argcomplete."""

    def __call__(self, *args: Any, **kwargs: Any) -> list[str]:
        return []


def files_completer() -> Any:
    """Devuelve un completer para archivos o un reemplazo inofensivo."""

    if _FilesCompleter is None:
        return _NoOpCompleter()
    return _FilesCompleter()


def directories_completer() -> Any:
    """Devuelve un completer para directorios o un reemplazo inofensivo."""

    if _DirectoriesCompleter is None:
        return _NoOpCompleter()
    return _DirectoriesCompleter()


def autocomplete_available() -> bool:
    """Indica si el soporte de autocompletado real está disponible."""

    return argcomplete is not None


def enable_autocomplete(parser: Any) -> bool:
    """Activa el autocompletado si argcomplete está disponible."""

    if argcomplete is None:
        return False
    argcomplete.autocomplete(parser)
    return True
