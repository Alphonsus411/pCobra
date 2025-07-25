import math


def sumar(a, b):
    """Suma dos valores."""
    return a + b


def promedio(valores):
    """Calcula el promedio de una lista de valores."""
    return sum(valores) / len(valores) if valores else 0


def potencia(base, exponente):
    """Eleva una base a un exponente."""
    return math.pow(base, exponente)
