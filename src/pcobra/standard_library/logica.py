"""Operaciones lógicas simples."""

from __future__ import annotations

from typing import Callable, Iterable, TypeVar

from pcobra.corelibs import logica as _logica

T = TypeVar("T")

__all__ = [
    "es_verdadero",
    "es_falso",
    "conjuncion",
    "disyuncion",
    "negacion",
    "entonces",
    "si_no",
    "condicional",
    "xor",
    "nand",
    "nor",
    "implica",
    "equivale",
    "xor_multiple",
    "todas",
    "alguna",
    "ninguna",
    "solo_uno",
    "conteo_verdaderos",
    "paridad",
]


def es_verdadero(valor: bool) -> bool:
    """Replica ``operator.truth`` validando que el argumento sea booleano."""

    return _logica.es_verdadero(valor)


def es_falso(valor: bool) -> bool:
    """Replica ``operator.not_`` validando que el argumento sea booleano."""

    return _logica.es_falso(valor)


def conjuncion(a: bool, b: bool) -> bool:
    """Retorna ``True`` si ambos argumentos son verdaderos."""

    return _logica.conjuncion(a, b)


def disyuncion(a: bool, b: bool) -> bool:
    """Retorna ``True`` si al menos uno de los argumentos es verdadero."""

    return _logica.disyuncion(a, b)


def negacion(valor: bool) -> bool:
    """Devuelve el opuesto lógico de ``valor``."""

    return _logica.negacion(valor)


def entonces(valor: bool, resultado: T | Callable[[], T]) -> T | None:
    """Devuelve *resultado* cuando ``valor`` es verdadero.

    Si se pasa un callable, su ejecución es diferida hasta que la condición
    resulta verdadera, evitando efectos secundarios innecesarios.
    """

    return _logica.entonces(valor, resultado)


def si_no(valor: bool, resultado: T | Callable[[], T]) -> T | None:
    """Devuelve *resultado* solo cuando ``valor`` es falso.

    Permite trabajar con callables diferidos, análogo a ``takeUnless`` en
    Kotlin y útil para encapsular lógica opcional.
    """

    return _logica.si_no(valor, resultado)


def condicional(
    *casos: tuple[bool | Callable[[], bool], T | Callable[[], T]],
    por_defecto: T | Callable[[], T] | None = None,
) -> T | None:
    """Evalúa pares ``(condición, resultado)`` al estilo ``when`` de Kotlin o ``case_when`` de R."""

    return _logica.condicional(*casos, por_defecto=por_defecto)


def xor(a: bool, b: bool) -> bool:
    """Retorna ``True`` cuando *a* y *b* difieren."""

    return _logica.xor(a, b)


def nand(a: bool, b: bool) -> bool:
    """Retorna el resultado de ``not (a and b)``."""

    return _logica.nand(a, b)


def nor(a: bool, b: bool) -> bool:
    """Retorna el resultado de ``not (a or b)``."""

    return _logica.nor(a, b)


def implica(antecedente: bool, consecuente: bool) -> bool:
    """Implementa la implicación lógica ``antecedente → consecuente``."""

    return _logica.implica(antecedente, consecuente)


def equivale(a: bool, b: bool) -> bool:
    """Retorna ``True`` cuando ambos argumentos comparten el mismo valor."""

    return _logica.equivale(a, b)


def xor_multiple(*valores: bool) -> bool:
    """Aplica XOR de manera acumulada sobre todos los argumentos."""

    return _logica.xor_multiple(*valores)


def todas(valores: Iterable[bool]) -> bool:
    """Valida que todos los elementos de *valores* sean verdaderos."""

    return _logica.todas(valores)


def alguna(valores: Iterable[bool]) -> bool:
    """Valida que al menos un elemento de *valores* sea verdadero."""

    return _logica.alguna(valores)


def ninguna(valores: Iterable[bool]) -> bool:
    """Devuelve ``True`` cuando ningún elemento es verdadero (equivalente a ``none``)."""

    return _logica.ninguna(valores)


def solo_uno(*valores: bool) -> bool:
    """Retorna ``True`` si exactamente un argumento es verdadero (equivalente a ``one?``)."""

    return _logica.solo_uno(*valores)


def conteo_verdaderos(valores: Iterable[bool]) -> int:
    """Cuenta cuántos elementos son verdaderos (equivalente a ``count``)."""

    return _logica.conteo_verdaderos(valores)


def paridad(valores: Iterable[bool]) -> bool:
    """Informa si la cantidad de verdaderos es par, como usar ``count`` y comprobar ``% 2``."""

    return _logica.paridad(valores)

