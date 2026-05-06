"""Superficie pública saneada para Holobit en runtime Python."""

from importlib import import_module
from typing import Any

__all__ = [
    "crear_holobit",
    "validar_holobit",
    "serializar_holobit",
    "deserializar_holobit",
    "proyectar",
    "transformar",
    "graficar",
    "combinar",
    "medir",
]


def __getattr__(name: str) -> Any:
    if name not in __all__:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    modulo = import_module("pcobra.corelibs.holobit")
    return getattr(modulo, name)
