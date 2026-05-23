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

PUBLIC_API_HOLOBIT: tuple[str, ...] = (
    "crear_holobit",
    "validar_holobit",
    "serializar_holobit",
    "deserializar_holobit",
    "proyectar",
    "transformar",
    "graficar",
    "combinar",
    "medir",
)


def _validar_superficie_publica_holobit() -> None:
    if tuple(__all__) != PUBLIC_API_HOLOBIT:
        raise RuntimeError(
            "[STARTUP CONTRACT] core.holobits.__all__ debe exponer únicamente la API pública canónica de Cobra."
        )


_validar_superficie_publica_holobit()


def __getattr__(name: str) -> Any:
    if name not in __all__:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    modulo = import_module("pcobra.corelibs.holobit")
    return getattr(modulo, name)
