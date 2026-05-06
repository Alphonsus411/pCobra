"""Fachada de red segura con API canónica en español."""

from pcobra.corelibs.red import (
    obtener_url,
    enviar_post,
    obtener_url_async,
    enviar_post_async,
    descargar_archivo,
    obtener_json,
)

__all__ = [
    "obtener_url",
    "enviar_post",
    "obtener_url_async",
    "enviar_post_async",
    "descargar_archivo",
    "obtener_json",

    "obtener_url_texto",]


def obtener_url(*args, **kwargs):
    """Delega en ``pcobra.corelibs.red.obtener_url``."""

    return _red.obtener_url(*args, **kwargs)


def enviar_post(*args, **kwargs):
    """Delega en ``pcobra.corelibs.red.enviar_post``."""

    return _red.enviar_post(*args, **kwargs)


def obtener_url_async(*args, **kwargs):
    """Delega en ``pcobra.corelibs.red.obtener_url_async``."""

    return _red.obtener_url_async(*args, **kwargs)


def enviar_post_async(*args, **kwargs):
    """Delega en ``pcobra.corelibs.red.enviar_post_async``."""

    return _red.enviar_post_async(*args, **kwargs)


def descargar_archivo(*args, **kwargs):
    """Delega en ``pcobra.corelibs.red.descargar_archivo``."""

    return _red.descargar_archivo(*args, **kwargs)


def obtener_url_texto(*args, **kwargs):
    """Delega en ``pcobra.corelibs.red.obtener_url_texto``."""

    return _red.obtener_url_texto(*args, **kwargs)


def obtener_json(*args, **kwargs):
    """Delega en ``pcobra.corelibs.red.obtener_json``."""

    return _red.obtener_json(*args, **kwargs)
