"""Funciones para realizar peticiones de red básicas."""

import os
import urllib.parse

import requests


def obtener_url(url: str) -> str:
    """Devuelve el contenido de una URL como texto."""
    url_baja = url.lower()
    if not (url_baja.startswith("http://") or url_baja.startswith("https://")):
        raise ValueError("Esquema de URL no soportado")
    allowed = os.environ.get("COBRA_HOST_WHITELIST")
    if allowed:
        hosts = {h.strip() for h in allowed.split(',') if h.strip()}
        host = urllib.parse.urlparse(url).hostname
        if host not in hosts:
            raise ValueError("Host no permitido")
    resp = requests.get(url, timeout=5)
    resp.raise_for_status()
    return resp.text


def enviar_post(url: str, datos: dict) -> str:
    """Envía datos por POST y retorna la respuesta."""
    url_baja = url.lower()
    if not (url_baja.startswith("http://") or url_baja.startswith("https://")):
        raise ValueError("Esquema de URL no soportado")
    allowed = os.environ.get("COBRA_HOST_WHITELIST")
    if allowed:
        hosts = {h.strip() for h in allowed.split(',') if h.strip()}
        host = urllib.parse.urlparse(url).hostname
        if host not in hosts:
            raise ValueError("Host no permitido")
    resp = requests.post(url, data=datos, timeout=5)
    resp.raise_for_status()
    return resp.text
