"""Puente canónico de runtime bajo ``pcobra.cobra.core``.

Este módulo reexporta primitivas de runtime históricamente ubicadas en
``pcobra.core`` para que la capa CLI pueda depender de un namespace interno
canónico (``pcobra.cobra.*``) sin modificar la implementación base.
"""

from __future__ import annotations

from typing import Any

from pcobra.core.interpreter import InterpretadorCobra
from pcobra.core.resource_limits import limitar_cpu_segundos, limitar_memoria_mb
from pcobra.core.semantic_validators import PrimitivaPeligrosaError, construir_cadena
from pcobra.core.semantic_validators.base import ValidadorBase

__all__ = [
    "InterpretadorCobra",
    "PrimitivaPeligrosaError",
    "SecurityError",
    "ValidadorBase",
    "construir_cadena",
    "ejecutar_en_contenedor",
    "ejecutar_en_sandbox",
    "limitar_cpu_segundos",
    "limitar_memoria_mb",
    "validar_dependencias",
]


def __getattr__(name: str) -> Any:
    """Resuelve símbolos de sandbox de forma perezosa para preservar fallback legacy."""

    if name in {
        "SecurityError",
        "ejecutar_en_contenedor",
        "ejecutar_en_sandbox",
        "validar_dependencias",
    }:
        from pcobra.core import sandbox as _sandbox

        return getattr(_sandbox, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
