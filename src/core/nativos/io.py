import os
import urllib.parse
from pathlib import Path

import requests


_MAX_RESP_SIZE = 1024 * 1024


def _leer_respuesta(resp: requests.Response) -> str:
    datos = bytearray()
    for chunk in resp.iter_content(chunk_size=8192):
        datos.extend(chunk)
        if len(datos) > _MAX_RESP_SIZE:
            raise ValueError("Respuesta demasiado grande")
    return datos.decode(resp.encoding or "utf-8", errors="replace")


def _resolver_ruta(ruta: str) -> Path:
    """Resuelve ``ruta`` dentro de un directorio permitido."""
    base = Path(os.environ.get("COBRA_IO_BASE_DIR") or Path.cwd()).resolve()
    p = Path(ruta)
    if p.is_absolute():
        raise ValueError("Ruta absoluta no permitida")
    if ".." in p.parts:
        raise ValueError("La ruta no puede contener '..'")
    destino = (base / p).resolve()
    try:
        destino.relative_to(base)
    except ValueError as exc:
        raise ValueError("Ruta fuera del directorio permitido") from exc
    return destino


def leer_archivo(ruta):
    """Devuelve el contenido de un archivo de texto."""
    ruta_segura = _resolver_ruta(ruta)
    with open(ruta_segura, "r", encoding="utf-8") as f:
        return f.read()


def escribir_archivo(ruta, datos):
    """Escribe datos en un archivo de texto."""
    ruta_segura = _resolver_ruta(ruta)
    with open(ruta_segura, "w", encoding="utf-8") as f:
        f.write(datos)


def _validar_host(url: str, hosts: set[str]) -> None:
    host = urllib.parse.urlparse(url).hostname
    if host not in hosts:
        raise ValueError("Host no permitido")


def obtener_url(url, permitir_redirecciones: bool = False):
    """Devuelve el contenido de una URL ``https://`` como texto.

    Es obligatorio definir la variable de entorno ``COBRA_HOST_WHITELIST`` con
    la lista de hosts permitidos separados por comas. Las redirecciones están
    deshabilitadas por defecto. Si se permiten, se valida que el destino final
    continúe dentro de la lista blanca de hosts.
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
    resp = requests.get(
        url, timeout=5, allow_redirects=permitir_redirecciones, stream=True
    )
    try:
        resp.raise_for_status()
        _validar_host(resp.url, hosts)
        return _leer_respuesta(resp)
    finally:
        resp.close()
