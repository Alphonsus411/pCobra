"""Operaciones lógicas simples."""

from __future__ import annotations

from typing import Iterable

from pcobra.corelibs import logica as _logica


def conjuncion(a: bool, b: bool) -> bool:
    """Retorna ``True`` si ambos argumentos son verdaderos."""

    return _logica.conjuncion(a, b)


def disyuncion(a: bool, b: bool) -> bool:
    """Retorna ``True`` si al menos uno de los argumentos es verdadero."""

    return _logica.disyuncion(a, b)


def negacion(valor: bool) -> bool:
    """Devuelve el opuesto lógico de ``valor``."""

    return _logica.negacion(valor)


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

