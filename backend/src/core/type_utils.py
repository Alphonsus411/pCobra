# coding: utf-8
"""Funciones auxiliares para verificacion de tipos en operaciones."""

from typing import Any


def verificar_sumables(a: Any, b: Any) -> None:
    """Asegura que ``a`` y ``b`` se puedan sumar."""
    if isinstance(a, (int, float)) and isinstance(b, (int, float)):
        return
    if isinstance(a, str) and isinstance(b, str):
        return
    raise TypeError(
        f"No se puede sumar valores de tipos {type(a).__name__} y {type(b).__name__}"
    )


def verificar_numeros(a: Any, b: Any, operador: str) -> None:
    """Valida que ambos operandos sean num\xc3\xa9ricos."""
    if not isinstance(a, (int, float)) or not isinstance(b, (int, float)):
        raise TypeError(f"Operaci\xc3\xb3n '{operador}' requiere operandos num\xc3\xa9ricos")


def verificar_comparables(a: Any, b: Any, operador: str) -> None:
    """Valida que los operandos sean comparables."""
    if isinstance(a, (int, float)) and isinstance(b, (int, float)):
        return
    if type(a) is type(b):
        return
    raise TypeError(
        f"Operaci\xc3\xb3n '{operador}' requiere operandos comparables"
    )


def verificar_booleanos(a: Any, b: Any, operador: str) -> None:
    """Valida que ambos operandos sean booleanos."""
    if not isinstance(a, bool) or not isinstance(b, bool):
        raise TypeError(f"Operaci\xc3\xb3n l\xc3\xb3gica '{operador}' requiere booleanos")


def verificar_booleano(a: Any, operador: str) -> None:
    """Valida que el operando sea booleano."""
    if not isinstance(a, bool):
        raise TypeError(f"Operaci\xc3\xb3n l\xc3\xb3gica '{operador}' requiere booleano")

