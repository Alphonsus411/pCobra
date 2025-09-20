"""Atajos numéricos de la biblioteca estándar."""

from __future__ import annotations

from typing import Iterable, SupportsFloat

from pcobra.corelibs import numero as _numero

RealLike = SupportsFloat | int | float

__all__ = [
    "es_finito",
    "es_infinito",
    "es_nan",
    "copiar_signo",
    "raiz_entera",
    "combinaciones",
    "permutaciones",
    "suma_precisa",
    "interpolar",
    "envolver_modular",
]


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


def raiz_entera(valor: RealLike) -> int:
    """Calcula la raíz cuadrada entera de ``valor`` usando ``math.isqrt``."""

    return _numero.raiz_entera(valor)


def combinaciones(n: int, k: int) -> int:
    """Equivale a ``math.comb`` para contar subconjuntos sin repetición."""

    return _numero.combinaciones(n, k)


def permutaciones(n: int, k: int | None = None) -> int:
    """Obtiene las permutaciones de ``n`` elementos tomando ``k`` posiciones."""

    return _numero.permutaciones(n, k)


def suma_precisa(valores: Iterable[RealLike]) -> float:
    """Suma ``valores`` con precisión extendida equivalente a ``math.fsum``."""

    return _numero.suma_precisa(valores)


def interpolar(inicio: RealLike, fin: RealLike, factor: RealLike) -> float:
    """Interpola linealmente siguiendo ``lerp`` de Rust/Kotlin."""

    return _numero.interpolar(inicio, fin, factor)


def envolver_modular(valor: RealLike, modulo: RealLike) -> float | int:
    """Aplica una envoltura modular como ``rem_euclid``/``mod``."""

    return _numero.envolver_modular(valor, modulo)
