# coding: utf-8
"""Módulo de compatibilidad para el antiguo validador semántico."""

from core.semantic_validators import (
    PrimitivaPeligrosaError,
    ValidadorPrimitivaPeligrosa,
    construir_cadena,
)

# Mantener nombre histórico
ValidadorSemantico = ValidadorPrimitivaPeligrosa

__all__ = ["PrimitivaPeligrosaError", "ValidadorSemantico", "construir_cadena"]
