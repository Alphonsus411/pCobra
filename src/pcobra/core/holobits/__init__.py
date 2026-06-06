"""Superficie pública saneada para Holobit en runtime Python."""

from importlib import import_module
from typing import Any

__all__ = [
    "Holobit",
    "crear_holobit",
    "validar_holobit",
    "serializar_holobit",
    "deserializar_holobit",
    "proyectar",
    "transformar",
    "graficar",
    "escalar",
    "mover",
    "combinar",
    "medir",
]

PUBLIC_API_HOLOBIT: tuple[str, ...] = (
    "Holobit",
    "crear_holobit",
    "validar_holobit",
    "serializar_holobit",
    "deserializar_holobit",
    "proyectar",
    "transformar",
    "graficar",
    "escalar",
    "mover",
    "combinar",
    "medir",
)

_LEGACY_EXPORT_MODULES: dict[str, str] = {
    "Holobit": "pcobra.core.holobits.holobit",
    "proyectar": "pcobra.core.holobits.proyeccion",
    "transformar": "pcobra.core.holobits.transformacion",
    "escalar": "pcobra.core.holobits.transformacion",
    "mover": "pcobra.core.holobits.transformacion",
    "graficar": "pcobra.core.holobits.graficar",
}


def _validar_superficie_publica_holobit() -> None:
    if tuple(__all__) != PUBLIC_API_HOLOBIT:
        raise RuntimeError(
            "[STARTUP CONTRACT] core.holobits.__all__ debe exponer únicamente la API pública canónica de Cobra."
        )


_validar_superficie_publica_holobit()


def __getattr__(name: str) -> Any:
    if name not in __all__:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    module_name = _LEGACY_EXPORT_MODULES.get(name, "pcobra.corelibs.holobit")
    modulo = import_module(module_name)
    return getattr(modulo, name)
