"""Fachada temporal en español para `usar \"tiempo\"`."""

from pcobra.corelibs.tiempo import ahora, formatear, dormir, epoch, desde_epoch

__all__ = ["ahora", "formatear", "dormir", "epoch", "desde_epoch"]


def ahora(*args, **kwargs):
    """Delega en ``pcobra.corelibs.tiempo.ahora``."""

    return _tiempo.ahora(*args, **kwargs)


def formatear(*args, **kwargs):
    """Delega en ``pcobra.corelibs.tiempo.formatear``."""

    return _tiempo.formatear(*args, **kwargs)


def dormir(*args, **kwargs):
    """Delega en ``pcobra.corelibs.tiempo.dormir``."""

    return _tiempo.dormir(*args, **kwargs)


def epoch(*args, **kwargs):
    """Delega en ``pcobra.corelibs.tiempo.epoch``."""

    return _tiempo.epoch(*args, **kwargs)


def desde_epoch(*args, **kwargs):
    """Delega en ``pcobra.corelibs.tiempo.desde_epoch``."""

    return _tiempo.desde_epoch(*args, **kwargs)
