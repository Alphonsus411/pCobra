"""Cadena de validadores semánticos para el modo seguro de Cobra."""

from __future__ import annotations

import sys

from types import FunctionType

from .primitiva_peligrosa import (
    PrimitivaPeligrosaError,
    ValidadorPrimitivaPeligrosa,
)
from .auditoria import ValidadorAuditoria
from .import_seguro import ValidadorImportSeguro
from .fs_access import ValidadorSistemaArchivos
from .reflexion_segura import ValidadorProhibirReflexion
from ..cobra_config import auditoria_activa

# Instancia por defecto reutilizable de la cadena de validación
_CADENA_DEFECTO = None
_CACHE_INFO: tuple[FunctionType, bool] | None = None


def construir_cadena(extra_validators=None):
    """Devuelve la cadena de validadores por defecto.

    Si no se proporcionan validadores extra, la cadena se crea una única vez y
    se reutiliza en llamadas sucesivas.
    """
    global _CADENA_DEFECTO, _CACHE_INFO

    auditoria = auditoria_activa()

    if (
        extra_validators is None
        and _CADENA_DEFECTO is not None
        and _CACHE_INFO == (ValidadorPrimitivaPeligrosa.__init__, auditoria)
    ):
        return _CADENA_DEFECTO

    if auditoria:
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
        _CACHE_INFO = (ValidadorPrimitivaPeligrosa.__init__, auditoria)

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

sys.modules["core.semantic_validators"] = sys.modules[__name__]
