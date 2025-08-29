"""Utilidades para manejar listas."""

from __future__ import annotations


def cabeza(lista):
    """Devuelve el primer elemento de ``lista`` o ``None`` si está vacía."""
    return lista[0] if lista else None


def cola(lista):
    """Retorna una copia de ``lista`` sin el primer elemento."""
    return list(lista[1:]) if len(lista) > 1 else []


def longitud(lista) -> int:
    """Número de elementos en ``lista``."""
    return len(lista)


def combinar(*listas):
    """Concatena varias listas en una nueva."""
    resultado = []
    for l in listas:
        resultado.extend(l)
    return resultado

