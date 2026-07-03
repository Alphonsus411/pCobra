"""Códigos de salida públicos para la CLI de Cobra."""

from __future__ import annotations

from enum import IntEnum


class CobraExitCode(IntEnum):
    """Códigos de salida estables usados por comandos CLI públicos."""

    SUCCESS = 0
    INVALID_PROJECT = 10
    MISSING_DEPENDENCY = 11
    VERSION_CONFLICT = 12
    HASH_MISMATCH = 13
    PYINSTALLER_UNAVAILABLE = 14
    INVALID_TARGET = 15
    UNEXPECTED_INTERNAL_ERROR = 70


__all__ = ["CobraExitCode"]
