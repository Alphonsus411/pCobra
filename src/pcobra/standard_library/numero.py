"""Atajos numéricos de la biblioteca estándar."""

from __future__ import annotations

from typing import SupportsFloat

from pcobra.corelibs import numero as _numero

RealLike = SupportsFloat | int | float

__all__ = ["es_finito", "es_infinito", "es_nan", "copiar_signo"]


def es_finito(valor: RealLike) -> bool:
    """Retorna ``True`` si ``valor`` es finito evitando `NaN` e infinitos."""

    return _numero.es_finito(valor)


def es_infinito(valor: RealLike) -> bool:
    """Retorna ``True`` si ``valor`` representa ``+∞`` o ``-∞``."""

    return _numero.es_infinito(valor)


def es_nan(valor: RealLike) -> bool:
    """Retorna ``True`` cuando ``valor`` es ``NaN`` conforme a IEEE-754."""

    return _numero.es_nan(valor)


def copiar_signo(magnitud: RealLike, signo: RealLike) -> float:
    """Devuelve ``magnitud`` con el signo de ``signo`` manteniendo ceros con signo."""

    return _numero.copiar_signo(magnitud, signo)
