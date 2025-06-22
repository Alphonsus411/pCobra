"""Cadena de validadores semánticos para el modo seguro de Cobra."""

from .primitiva_peligrosa import (
    PrimitivaPeligrosaError,
    ValidadorPrimitivaPeligrosa,
)
from .import_seguro import ValidadorImportSeguro

# Instancia por defecto reutilizable de la cadena de validación
_CADENA_DEFECTO = None


def construir_cadena(extra_validators=None):
    """Devuelve la cadena de validadores por defecto.

    Si no se proporcionan validadores extra, la cadena se crea una única vez y
    se reutiliza en llamadas sucesivas.
    """
    global _CADENA_DEFECTO

    if extra_validators is None and _CADENA_DEFECTO is not None:
        return _CADENA_DEFECTO

    primero = ValidadorPrimitivaPeligrosa()
    actual = primero.set_siguiente(ValidadorImportSeguro())

    if extra_validators:
        for val in extra_validators:
            actual = actual.set_siguiente(val)

    if extra_validators is None:
        _CADENA_DEFECTO = primero

    return primero

__all__ = [
    "PrimitivaPeligrosaError",
    "ValidadorPrimitivaPeligrosa",
    "ValidadorImportSeguro",
    "construir_cadena",
]
