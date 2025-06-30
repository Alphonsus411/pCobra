"""Operaciones numéricas comunes."""


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
