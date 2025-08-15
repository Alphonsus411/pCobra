"""Funciones para realizar peticiones de red básicas."""

import os
import urllib.parse

import requests


def _validar_host(url: str, hosts: set[str]) -> None:
    host = urllib.parse.urlparse(url).hostname
    if host not in hosts:
        raise ValueError("Host no permitido")


def obtener_url(url: str, permitir_redirecciones: bool = False) -> str:
    """Devuelve el contenido de una URL ``https://`` como texto.

    Las redirecciones están deshabilitadas por defecto. Si se permiten,
    se valida que el destino final continúe dentro de la lista blanca de hosts.
    """
    url_baja = url.lower()
    if not url_baja.startswith("https://"):
        raise ValueError("Esquema de URL no soportado")
    allowed = os.environ.get("COBRA_HOST_WHITELIST")
    if not allowed:
        raise ValueError("COBRA_HOST_WHITELIST no establecido")
    hosts = {h.strip() for h in allowed.split(',') if h.strip()}
    if not hosts:
        raise ValueError("COBRA_HOST_WHITELIST vacío")
    _validar_host(url, hosts)
    resp = requests.get(url, timeout=5, allow_redirects=permitir_redirecciones)
    resp.raise_for_status()
    if permitir_redirecciones:
        if not resp.url.lower().startswith("https://"):
            raise ValueError("Esquema de URL no soportado")
        _validar_host(resp.url, hosts)
    return resp.text


def enviar_post(url: str, datos: dict, permitir_redirecciones: bool = False) -> str:
    """Envía datos por ``POST`` a una URL ``https://`` y retorna la respuesta.

    Las redirecciones están deshabilitadas por defecto. Si se permiten,
    se valida que el destino final continúe dentro de la lista blanca de hosts.
    """
    url_baja = url.lower()
    if not url_baja.startswith("https://"):
        raise ValueError("Esquema de URL no soportado")
    allowed = os.environ.get("COBRA_HOST_WHITELIST")
    if not allowed:
        raise ValueError("COBRA_HOST_WHITELIST no establecido")
    hosts = {h.strip() for h in allowed.split(',') if h.strip()}
    if not hosts:
        raise ValueError("COBRA_HOST_WHITELIST vacío")
    _validar_host(url, hosts)
    resp = requests.post(
        url, data=datos, timeout=5, allow_redirects=permitir_redirecciones
    )
    resp.raise_for_status()
    if permitir_redirecciones:
        if not resp.url.lower().startswith("https://"):
            raise ValueError("Esquema de URL no soportado")
        _validar_host(resp.url, hosts)
    return resp.text
