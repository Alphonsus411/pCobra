"""Cadena de validadores semánticos para el modo seguro de Cobra."""

from core.semantic_validators.primitiva_peligrosa import (
    PrimitivaPeligrosaError,
    ValidadorPrimitivaPeligrosa,
)
from core.semantic_validators.auditoria import ValidadorAuditoria
from core.semantic_validators.import_seguro import ValidadorImportSeguro
from core.semantic_validators.fs_access import ValidadorSistemaArchivos
from core.semantic_validators.reflexion_segura import ValidadorProhibirReflexion
from core.cobra_config import auditoria_activa

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

    if auditoria_activa():
        primero = ValidadorAuditoria()
        actual = primero.set_siguiente(ValidadorPrimitivaPeligrosa())
    else:
        primero = ValidadorPrimitivaPeligrosa()
        actual = primero
    actual = actual.set_siguiente(ValidadorImportSeguro())
    actual = actual.set_siguiente(ValidadorSistemaArchivos())
    actual = actual.set_siguiente(ValidadorProhibirReflexion())

    if extra_validators:
        for val in extra_validators:
            actual = actual.set_siguiente(val)

    if extra_validators is None:
        _CADENA_DEFECTO = primero

    return primero

__all__ = [
    "PrimitivaPeligrosaError",
    "ValidadorPrimitivaPeligrosa",
    "ValidadorAuditoria",
    "ValidadorImportSeguro",
    "ValidadorSistemaArchivos",
    "ValidadorProhibirReflexion",
    "construir_cadena",
]
