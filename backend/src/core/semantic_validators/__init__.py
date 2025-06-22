"""Cadena de validadores semánticos para el modo seguro de Cobra."""

from .primitiva_peligrosa import PrimitivaPeligrosaError, ValidadorPrimitivaPeligrosa
from .import_seguro import ValidadorImportSeguro


def construir_cadena(extra_validators=None):
    """Construye la cadena de validadores por defecto."""
    primero = ValidadorPrimitivaPeligrosa()
    actual = primero.set_siguiente(ValidadorImportSeguro())

    if extra_validators:
        for val in extra_validators:
            actual = actual.set_siguiente(val)

    return primero

__all__ = [
    "PrimitivaPeligrosaError",
    "ValidadorPrimitivaPeligrosa",
    "ValidadorImportSeguro",
    "construir_cadena",
]
