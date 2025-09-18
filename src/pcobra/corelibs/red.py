"""Funciones para realizar peticiones de red básicas."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any
import urllib.parse

import httpx
import requests


_MAX_RESP_SIZE = 1024 * 1024
_MAX_REDIRECTS = 5


def _obtener_hosts_permitidos() -> set[str]:
    allowed = os.environ.get("COBRA_HOST_WHITELIST")
    if not allowed:
        raise ValueError("COBRA_HOST_WHITELIST no establecido")
    hosts = {h.strip().lower() for h in allowed.split(',') if h.strip()}
    if not hosts:
        raise ValueError("COBRA_HOST_WHITELIST vacío")
    return hosts


def _validar_esquema(url: str) -> None:
    if not url.lower().startswith("https://"):
        raise ValueError("Esquema de URL no soportado")


def _leer_respuesta(resp: requests.Response) -> str:
    datos = bytearray()
    for chunk in resp.iter_content(chunk_size=8192):
        datos.extend(chunk)
        if len(datos) > _MAX_RESP_SIZE:
            raise ValueError("Respuesta demasiado grande")
    return datos.decode(resp.encoding or "utf-8", errors="replace")


def _validar_host(url: str, hosts: set[str]) -> None:
    host = urllib.parse.urlparse(url).hostname
    host_normalizado = host.lower() if host else None
    if not host_normalizado or host_normalizado not in hosts:
        raise ValueError("Host no permitido")


def _resolver_redireccion(
    url_actual: str, destino: str | None, hosts: set[str]
) -> str:
    if not destino:
        raise ValueError("Redirección sin encabezado Location")
    nueva_url = urllib.parse.urljoin(url_actual, destino)
    _validar_esquema(nueva_url)
    _validar_host(nueva_url, hosts)
    return nueva_url


def obtener_url(url: str, permitir_redirecciones: bool = False) -> str:
    """Devuelve el contenido de una URL ``https://`` como texto.

    Las redirecciones están deshabilitadas por defecto. Si se permiten,
    se siguen manualmente tras validar que cada salto permanezca en la lista
    blanca de hosts autorizados.
    """
    _validar_esquema(url)
    hosts = _obtener_hosts_permitidos()
    url_actual = url
    redirecciones_restantes = _MAX_REDIRECTS
    while True:
        _validar_host(url_actual, hosts)
        resp = requests.get(
            url_actual, timeout=5, allow_redirects=False, stream=True
        )
        if permitir_redirecciones and 300 <= resp.status_code < 400:
            if redirecciones_restantes == 0:
                resp.close()
                raise ValueError("Demasiadas redirecciones")
            destino = resp.headers.get("Location")
            try:
                nueva_url = _resolver_redireccion(url_actual, destino, hosts)
            finally:
                resp.close()
            url_actual = nueva_url
            redirecciones_restantes -= 1
            continue
        try:
            resp.raise_for_status()
            _validar_esquema(resp.url)
            _validar_host(resp.url, hosts)
            return _leer_respuesta(resp)
        finally:
            resp.close()


def enviar_post(url: str, datos: dict, permitir_redirecciones: bool = False) -> str:
    """Envía datos por ``POST`` a una URL ``https://`` y retorna la respuesta.

    Las redirecciones están deshabilitadas por defecto. Si se permiten,
    se siguen manualmente tras validar que cada salto permanezca en la lista
    blanca de hosts autorizados.
    """
    _validar_esquema(url)
    hosts = _obtener_hosts_permitidos()
    url_actual = url
    redirecciones_restantes = _MAX_REDIRECTS
    while True:
        _validar_host(url_actual, hosts)
        resp = requests.post(
            url_actual,
            data=datos,
            timeout=5,
            allow_redirects=False,
            stream=True,
        )
        if permitir_redirecciones and 300 <= resp.status_code < 400:
            if redirecciones_restantes == 0:
                resp.close()
                raise ValueError("Demasiadas redirecciones")
            destino = resp.headers.get("Location")
            try:
                nueva_url = _resolver_redireccion(url_actual, destino, hosts)
            finally:
                resp.close()
            url_actual = nueva_url
            redirecciones_restantes -= 1
            continue
        try:
            resp.raise_for_status()
            _validar_esquema(resp.url)
            _validar_host(resp.url, hosts)
            return _leer_respuesta(resp)
        finally:
            resp.close()


async def _leer_respuesta_async(resp: httpx.Response) -> str:
    datos = bytearray()
    async for chunk in resp.aiter_bytes(chunk_size=8192):
        datos.extend(chunk)
        if len(datos) > _MAX_RESP_SIZE:
            raise ValueError("Respuesta demasiado grande")
    return datos.decode(resp.encoding or "utf-8", errors="replace")


async def _descargar_a_archivo(resp: httpx.Response, destino: Path) -> Path:
    total = 0
    with destino.open("wb") as archivo:
        async for chunk in resp.aiter_bytes(chunk_size=8192):
            total += len(chunk)
            if total > _MAX_RESP_SIZE:
                raise ValueError("Respuesta demasiado grande")
            archivo.write(chunk)
    return destino


async def _realizar_peticion_async(
    metodo: str,
    url: str,
    *,
    datos: dict[str, Any] | None = None,
    permitir_redirecciones: bool = False,
    destino: Path | None = None,
) -> str | Path:
    _validar_esquema(url)
    hosts = _obtener_hosts_permitidos()
    url_actual = url
    redirecciones_restantes = _MAX_REDIRECTS
    async with httpx.AsyncClient(follow_redirects=False, timeout=5.0) as client:
        while True:
            _validar_host(url_actual, hosts)
            request_args: dict[str, Any] = {"data": datos} if datos is not None else {}
            async with client.stream(
                metodo, url_actual, follow_redirects=False, **request_args
            ) as resp:
                if permitir_redirecciones and 300 <= resp.status_code < 400:
                    if redirecciones_restantes == 0:
                        raise ValueError("Demasiadas redirecciones")
                    destino_header = resp.headers.get("Location")
                    url_actual = _resolver_redireccion(url_actual, destino_header, hosts)
                    redirecciones_restantes -= 1
                    continue
                resp.raise_for_status()
                url_final = str(resp.url)
                _validar_esquema(url_final)
                _validar_host(url_final, hosts)
                if destino is not None:
                    return await _descargar_a_archivo(resp, destino)
                return await _leer_respuesta_async(resp)


async def obtener_url_async(
    url: str, permitir_redirecciones: bool = False
) -> str:
    """Versión asíncrona de :func:`obtener_url`."""

    resultado = await _realizar_peticion_async(
        "GET", url, permitir_redirecciones=permitir_redirecciones
    )
    assert isinstance(resultado, str)
    return resultado


async def enviar_post_async(
    url: str, datos: dict[str, Any], permitir_redirecciones: bool = False
) -> str:
    """Versión asíncrona de :func:`enviar_post`."""

    resultado = await _realizar_peticion_async(
        "POST",
        url,
        datos=datos,
        permitir_redirecciones=permitir_redirecciones,
    )
    assert isinstance(resultado, str)
    return resultado


async def descargar_archivo(
    url: str,
    destino: str | os.PathLike[str],
    *,
    permitir_redirecciones: bool = False,
    crear_padres: bool = True,
) -> Path:
    """Descarga una URL ``https://`` a ``destino`` respetando la lista blanca."""

    ruta = Path(destino)
    if crear_padres:
        ruta.parent.mkdir(parents=True, exist_ok=True)
    try:
        resultado = await _realizar_peticion_async(
            "GET", url, permitir_redirecciones=permitir_redirecciones, destino=ruta
        )
    except Exception:
        if ruta.exists():
            ruta.unlink()
        raise
    assert isinstance(resultado, Path)
    return resultado
