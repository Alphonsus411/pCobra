import os
import urllib.parse

import requests


def leer_archivo(ruta):
    """Devuelve el contenido de un archivo de texto."""
    with open(ruta, "r", encoding="utf-8") as f:
        return f.read()


def escribir_archivo(ruta, datos):
    """Escribe datos en un archivo de texto."""
    with open(ruta, "w", encoding="utf-8") as f:
        f.write(datos)


def obtener_url(url):
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
