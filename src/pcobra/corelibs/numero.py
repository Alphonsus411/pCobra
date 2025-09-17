"""Operaciones numéricas comunes."""

from __future__ import annotations

import math
import random
from statistics import StatisticsError, median, mode, pstdev, stdev


def absoluto(valor):
    """Devuelve el valor absoluto de ``valor`` preservando el tipo de enteros."""

    resultado = math.fabs(valor)
    if isinstance(valor, int) and resultado.is_integer():
        return int(resultado)
    return resultado


def redondear(valor, ndigitos: int | None = None):
    """Redondea ``valor`` a ``ndigitos`` cifras decimales."""

    if ndigitos is None:
        return round(valor)
    return round(valor, ndigitos)


def piso(valor):
    """Equivalente a ``math.floor``."""

    return math.floor(valor)


def techo(valor):
    """Equivalente a ``math.ceil``."""

    return math.ceil(valor)


def raiz(valor, indice: float = 2):
    """Calcula la raíz ``indice``-ésima de ``valor``."""

    indice_float = float(indice)
    if indice_float == 0:
        raise ValueError("El índice de la raíz no puede ser cero")
    if valor < 0:
        if indice_float.is_integer():
            if int(indice_float) % 2 == 0:
                raise ValueError(
                    "No se puede calcular la raíz par de un número negativo"
                )
        else:
            raise ValueError(
                "No se puede calcular la raíz de índice fraccionario de un número negativo"
            )
    magnitud = math.pow(abs(valor), 1.0 / indice_float)
    return -magnitud if valor < 0 else magnitud


def potencia(base, exponente):
    """Eleva ``base`` a ``exponente`` utilizando ``math.pow``."""

    return math.pow(base, exponente)


def clamp(valor, minimo, maximo):
    """Restringe ``valor`` al rango ``[minimo, maximo]``."""

    if minimo > maximo:
        raise ValueError("El mínimo no puede ser mayor que el máximo")
    return max(min(valor, maximo), minimo)


def aleatorio(inicio: float = 0.0, fin: float = 1.0, semilla: int | None = None) -> float:
    """Genera un número aleatorio uniforme entre ``inicio`` y ``fin``."""

    if inicio > fin:
        raise ValueError("El inicio no puede ser mayor que el fin")
    if semilla is not None:
        generador = random.Random(semilla)
        return generador.uniform(inicio, fin)
    return random.uniform(inicio, fin)


def mediana(valores) -> float:
    """Calcula la mediana de ``valores`` usando :mod:`statistics`."""

    if not valores:
        raise ValueError("No se puede calcular la mediana de una secuencia vacía")
    return median(valores)


def moda(valores):
    """Calcula la moda de ``valores`` usando :mod:`statistics`."""

    if not valores:
        raise ValueError("No se puede calcular la moda de una secuencia vacía")
    try:
        return mode(valores)
    except StatisticsError as exc:  # pragma: no cover - comportamiento defensivo
        raise ValueError(str(exc)) from exc


def desviacion_estandar(valores, *, muestral: bool = False) -> float:
    """Obtiene la desviación estándar de ``valores``."""

    if not valores:
        raise ValueError("No se puede calcular la desviación estándar de una secuencia vacía")
    funcion = stdev if muestral else pstdev
    try:
        return funcion(valores)
    except StatisticsError as exc:  # pragma: no cover - comportamiento defensivo
        raise ValueError(str(exc)) from exc


def es_par(n: int) -> bool:
    """Retorna ``True`` si *n* es par."""
    return n % 2 == 0


def es_primo(n: int) -> bool:
    """Determina si *n* es un número primo."""
    if n <= 1:
        return False
    for i in range(2, int(n ** 0.5) + 1):
        if n % i == 0:
            return False
    return True


def factorial(n: int) -> int:
    """Calcula el factorial de *n*."""
    resultado = 1
    for i in range(1, n + 1):
        resultado *= i
    return resultado


def promedio(valores) -> float:
    """Calcula el promedio de una secuencia de valores."""
    return sum(valores) / len(valores) if valores else 0.0
