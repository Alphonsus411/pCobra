"""Atajos numéricos de la biblioteca estándar."""

from __future__ import annotations

from typing import Iterable, SupportsFloat, Tuple

from pcobra.corelibs import numero as _numero

RealLike = SupportsFloat | int | float

__all__ = [
    "es_finito",
    "es_infinito",
    "es_nan",
    "copiar_signo",
    "signo",
    "limitar",
    "hipotenusa",
    "distancia_euclidiana",
    "raiz_entera",
    "combinaciones",
    "permutaciones",
    "suma_precisa",
    "interpolar",
    "envolver_modular",
    "varianza",
    "varianza_muestral",
    "media_geometrica",
    "media_armonica",
    "percentil",
    "cuartiles",
    "rango_intercuartil",
    "coeficiente_variacion",
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


def signo(valor: RealLike) -> float | int:
    """Calcula el signo de ``valor`` devolviendo ``-1``, ``0`` o ``1`` y propagando ``NaN``."""

    return _numero.signo(valor)


def limitar(valor: RealLike, minimo: RealLike, maximo: RealLike) -> float | int:
    """Restringe ``valor`` al intervalo ``[minimo, maximo]`` validando los límites."""

    return _numero.limitar(valor, minimo, maximo)


def hipotenusa(*componentes: RealLike | Iterable[RealLike]) -> float:
    """Calcula la hipotenusa n-dimensional validando los componentes."""

    return _numero.hipotenusa(*componentes)


def distancia_euclidiana(
    punto_a: Iterable[RealLike], punto_b: Iterable[RealLike]
) -> float:
    """Obtiene la distancia euclidiana entre ``punto_a`` y ``punto_b``."""

    return _numero.distancia_euclidiana(punto_a, punto_b)


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


def varianza(valores: Iterable[RealLike]) -> float:
    """Calcula la varianza poblacional de ``valores``."""

    return _numero.varianza(valores)


def varianza_muestral(valores: Iterable[RealLike]) -> float:
    """Calcula la varianza muestral de ``valores``."""

    return _numero.varianza_muestral(valores)


def media_geometrica(valores: Iterable[RealLike]) -> float:
    """Devuelve la media geométrica de ``valores``."""

    return _numero.media_geometrica(valores)


def media_armonica(valores: Iterable[RealLike]) -> float:
    """Devuelve la media armónica de ``valores``."""

    return _numero.media_armonica(valores)


def percentil(valores: Iterable[RealLike], porcentaje: RealLike) -> float:
    """Calcula el percentil ``porcentaje`` mediante interpolación lineal."""

    return _numero.percentil(valores, porcentaje)


def cuartiles(valores: Iterable[RealLike]) -> Tuple[float, float, float]:
    """Devuelve los cuartiles ``Q1``, ``Q2`` y ``Q3`` de ``valores``."""

    return _numero.cuartiles(valores)


def rango_intercuartil(valores: Iterable[RealLike]) -> float:
    """Calcula el rango intercuartílico (``Q3 - Q1``)."""

    return _numero.rango_intercuartil(valores)


def coeficiente_variacion(
    valores: Iterable[RealLike],
    *,
    muestral: bool = False,
) -> float:
    """Calcula el coeficiente de variación de ``valores``."""

    return _numero.coeficiente_variacion(valores, muestral=muestral)
