"""Fachada pública Holobit para `usar \"holobit\"`."""

from pcobra.corelibs.holobit import (
    combinar,
    crear_holobit,
    deserializar_holobit,
    graficar,
    medir,
    proyectar,
    serializar_holobit,
    transformar,
    validar_holobit,
)

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
            "[STARTUP CONTRACT] standard_library.holobit.__all__ debe exponer únicamente la API pública canónica de Cobra."
        )


_validar_superficie_publica_holobit()
