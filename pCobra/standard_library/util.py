"""Pequeñas funciones de ayuda."""

from __future__ import annotations


def es_nulo(valor) -> bool:
    """Indica si ``valor`` es ``None``."""
    return valor is None


def es_vacio(secuencia) -> bool:
    """Devuelve ``True`` si la secuencia no contiene elementos."""
    return len(secuencia) == 0


def repetir(cadena: str, veces: int) -> str:
    """Retorna ``cadena`` repetida ``veces`` veces."""
    return cadena * veces

