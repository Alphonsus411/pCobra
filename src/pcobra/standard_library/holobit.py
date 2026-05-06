"""Fachada pública Holobit para `usar \"holobit\"`."""

from pcobra.corelibs.holobit import (
    crear_holobit,
    validar_holobit,
    serializar_holobit,
    deserializar_holobit,
    proyectar,
    transformar,
    graficar,
    combinar,
    medir,
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


def crear_holobit(*args, **kwargs):
    """Delega en ``pcobra.corelibs.holobit.crear_holobit``."""

    return _holobit.crear_holobit(*args, **kwargs)


def validar_holobit(*args, **kwargs):
    """Delega en ``pcobra.corelibs.holobit.validar_holobit``."""

    return _holobit.validar_holobit(*args, **kwargs)


def serializar_holobit(*args, **kwargs):
    """Delega en ``pcobra.corelibs.holobit.serializar_holobit``."""

    return _holobit.serializar_holobit(*args, **kwargs)


def deserializar_holobit(*args, **kwargs):
    """Delega en ``pcobra.corelibs.holobit.deserializar_holobit``."""

    return _holobit.deserializar_holobit(*args, **kwargs)


def proyectar(*args, **kwargs):
    """Delega en ``pcobra.corelibs.holobit.proyectar``."""

    return _holobit.proyectar(*args, **kwargs)


def transformar(*args, **kwargs):
    """Delega en ``pcobra.corelibs.holobit.transformar``."""

    return _holobit.transformar(*args, **kwargs)


def graficar(*args, **kwargs):
    """Delega en ``pcobra.corelibs.holobit.graficar``."""

    return _holobit.graficar(*args, **kwargs)


def combinar(*args, **kwargs):
    """Delega en ``pcobra.corelibs.holobit.combinar``."""

    return _holobit.combinar(*args, **kwargs)


def medir(*args, **kwargs):
    """Delega en ``pcobra.corelibs.holobit.medir``."""

    return _holobit.medir(*args, **kwargs)
