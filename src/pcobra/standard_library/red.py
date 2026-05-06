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
]
