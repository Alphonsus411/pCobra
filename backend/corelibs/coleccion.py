"""Funciones para trabajar con colecciones."""


def ordenar(lista):
    """Devuelve una copia ordenada de *lista*."""
    return sorted(lista)


def maximo(lista):
    """Devuelve el valor máximo de *lista*."""
    return max(lista)


def minimo(lista):
    """Devuelve el valor mínimo de *lista*."""
    return min(lista)


def sin_duplicados(lista):
    """Retorna una lista sin elementos duplicados manteniendo el orden."""
    return list(dict.fromkeys(lista))
