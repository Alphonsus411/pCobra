"""Operaciones lógicas simples."""

from __future__ import annotations


def conjuncion(a: bool, b: bool) -> bool:
    """Retorna ``True`` si ambos argumentos son verdaderos."""
    return bool(a and b)


def disyuncion(a: bool, b: bool) -> bool:
    """Retorna ``True`` si al menos uno de los argumentos es verdadero."""
    return bool(a or b)


def negacion(valor: bool) -> bool:
    """Devuelve el opuesto lógico de ``valor``."""
    return not valor

