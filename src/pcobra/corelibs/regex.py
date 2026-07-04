"""Funciones utilitarias para trabajar con expresiones regulares."""

from __future__ import annotations

import re
from collections.abc import Callable
from typing import Any

__all__ = [
    "buscar",
    "coincidir",
    "reemplazar",
    "dividir",
    "encontrar_todos",
]

_Reemplazo = str | Callable[[re.Match[str]], str]


def _validar_texto(valor: str, nombre_argumento: str) -> str:
    if not isinstance(valor, str):
        raise TypeError(f"{nombre_argumento} debe ser texto")
    return valor


def _error_patron(exc: re.error) -> ValueError:
    """Convierte errores de ``re`` en mensajes claros para Cobra."""

    return ValueError(f"patrón de expresión regular inválido: {exc}")


def buscar(patron: str, texto: str, *, flags: int = 0) -> str | None:
    """Busca ``patron`` en ``texto`` y devuelve el texto coincidente o ``None``."""

    try:
        coincidencia = re.search(
            _validar_texto(patron, "patron"), _validar_texto(texto, "texto"), flags
        )
    except re.error as exc:
        raise _error_patron(exc) from None
    if coincidencia is None:
        return None
    return coincidencia.group(0)


def coincidir(patron: str, texto: str, *, flags: int = 0) -> str | None:
    """Comprueba si ``texto`` empieza con ``patron`` y devuelve la coincidencia."""

    try:
        coincidencia = re.match(
            _validar_texto(patron, "patron"), _validar_texto(texto, "texto"), flags
        )
    except re.error as exc:
        raise _error_patron(exc) from None
    if coincidencia is None:
        return None
    return coincidencia.group(0)


def reemplazar(
    patron: str,
    reemplazo: _Reemplazo,
    texto: str,
    *,
    limite: int = 0,
    flags: int = 0,
) -> str:
    """Reemplaza coincidencias de ``patron`` en ``texto`` respetando ``limite``."""

    try:
        return re.sub(
            _validar_texto(patron, "patron"),
            reemplazo,
            _validar_texto(texto, "texto"),
            count=limite,
            flags=flags,
        )
    except re.error as exc:
        raise _error_patron(exc) from None


def dividir(patron: str, texto: str, *, maximo: int = 0, flags: int = 0) -> list[str]:
    """Divide ``texto`` usando ``patron`` como separador."""

    try:
        return re.split(
            _validar_texto(patron, "patron"),
            _validar_texto(texto, "texto"),
            maxsplit=maximo,
            flags=flags,
        )
    except re.error as exc:
        raise _error_patron(exc) from None


def encontrar_todos(patron: str, texto: str, *, flags: int = 0) -> list[Any]:
    """Devuelve una lista con todas las coincidencias de ``patron`` en ``texto``."""

    try:
        return list(
            re.findall(
                _validar_texto(patron, "patron"), _validar_texto(texto, "texto"), flags
            )
        )
    except re.error as exc:
        raise _error_patron(exc) from None
