"""Implementación parcial de :mod:`numpy` para entornos sin la dependencia."""

from __future__ import annotations

import math
from typing import Iterable, Sequence

nan = math.nan
number = (int, float)
floating = float
integer = int
bool_ = bool


class ndarray(list):
    """Representación simple compatible con las operaciones usadas en el proyecto."""

    def __init__(self, iterable: Iterable[float]):
        super().__init__(float(valor) for valor in iterable)

    def __iadd__(self, other: Iterable[float]) -> "ndarray":
        otros = list(float(v) for v in other)
        if len(otros) != len(self):
            raise ValueError("Las dimensiones no coinciden para la suma")
        for indice, valor in enumerate(otros):
            self[indice] += valor
        return self

    def __imul__(self, escalar: float) -> "ndarray":
        factor = float(escalar)
        for indice, valor in enumerate(self):
            self[indice] = valor * factor
        return self

    def tolist(self) -> list[float]:
        return list(self)


def array(valores: Iterable[float], dtype: type | None = float) -> ndarray:
    """Crea un :class:`ndarray` a partir de un iterable."""

    return ndarray(valores)


def allclose(a: Iterable[float], b: Iterable[float], rtol: float = 1e-08, atol: float = 1e-08) -> bool:
    """Comprueba si dos secuencias son aproximadamente iguales."""

    lista_a = list(float(valor) for valor in a)
    lista_b = list(float(valor) for valor in b)
    if len(lista_a) != len(lista_b):
        return False
    return all(math.isclose(va, vb, rel_tol=rtol, abs_tol=atol) for va, vb in zip(lista_a, lista_b))


def percentile(datos: Sequence[float], q: float, *, method: str = "linear") -> float:
    """Calcula el percentil ``q`` de ``datos`` usando interpolación lineal."""

    if method != "linear":  # pragma: no cover - solo se usa "linear" en tests
        raise ValueError("Solo se admite el método 'linear' en la implementación reducida")
    if not datos:
        raise ValueError("La secuencia de datos no puede estar vacía")

    valores = sorted(float(valor) for valor in datos)
    if q <= 0:
        return valores[0]
    if q >= 100:
        return valores[-1]

    posicion = (len(valores) - 1) * (q / 100.0)
    inferior = int(math.floor(posicion))
    superior = int(math.ceil(posicion))
    if inferior == superior:
        return valores[inferior]
    peso = posicion - inferior
    return valores[inferior] * (1.0 - peso) + valores[superior] * peso


def isnan(valor: float) -> bool:
    """Replica :func:`numpy.isnan` usando :mod:`math`."""

    try:
        return math.isnan(float(valor))
    except (TypeError, ValueError):  # pragma: no cover - mantener compatibilidad
        return False




def isscalar(valor: object) -> bool:
    """Replica ``numpy.isscalar`` de forma simplificada."""

    return not isinstance(valor, (list, tuple, set, dict))

__all__ = [
    "array",
    "allclose",
    "ndarray",
    "nan",
    "number",
    "floating",
    "integer",
    "bool_",
    "percentile",
    "isnan",
    "isscalar",
]
