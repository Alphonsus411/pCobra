"""Funciones para realizar peticiones de red básicas."""

import urllib.parse
import urllib.request


def obtener_url(url: str) -> str:
    """Devuelve el contenido de una URL como texto."""
    url_baja = url.lower()
    if not (url_baja.startswith("http://") or url_baja.startswith("https://")):
        raise ValueError("Esquema de URL no soportado")
    with urllib.request.urlopen(url, timeout=5) as resp:
        return resp.read().decode("utf-8")


def enviar_post(url: str, datos: dict) -> str:
    """Envía datos por POST y retorna la respuesta."""
    url_baja = url.lower()
    if not (url_baja.startswith("http://") or url_baja.startswith("https://")):
        raise ValueError("Esquema de URL no soportado")
    encoded = urllib.parse.urlencode(datos).encode()
    with urllib.request.urlopen(url, encoded, timeout=5) as resp:
        return resp.read().decode("utf-8")
