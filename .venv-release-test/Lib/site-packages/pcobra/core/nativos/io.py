import os
import sys
import urllib.parse
from pathlib import Path
from types import ModuleType

try:
    import requests
except ModuleNotFoundError as exc:  # pragma: no cover - entorno sin requests
    requests = ModuleType("requests")

    class _Response:  # pragma: no cover - interfaz mínima
        pass

    def _missing(*_args, **_kwargs):
        raise ModuleNotFoundError(
            "El módulo opcional 'requests' es necesario para realizar peticiones HTTP."
        ) from exc

    requests.Response = _Response
    requests.get = _missing
    requests.post = _missing
    sys.modules.setdefault("requests", requests)


# Mantener estos límites alineados con ``corelibs.red``.
_MAX_RESP_SIZE = 1024 * 1024
_MAX_REDIRECTS = 5


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


def _validar_esquema(url: str) -> None:
    if not url.lower().startswith("https://"):
        raise ValueError("Esquema de URL no soportado")


def _obtener_hosts_permitidos() -> set[str]:
    allowed = os.environ.get("COBRA_HOST_WHITELIST")
    if not allowed:
        raise ValueError("COBRA_HOST_WHITELIST no establecido")
    hosts = {h.strip().lower() for h in allowed.split(',') if h.strip()}
    if not hosts:
        raise ValueError("COBRA_HOST_WHITELIST vacío")
    return hosts


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


def obtener_url(url, permitir_redirecciones: bool = False):
    """Devuelve el contenido de una URL ``https://`` como texto.

    Las redirecciones se siguen manualmente solo si ``permitir_redirecciones``
    es ``True``. En cada salto se valida primero el esquema (debe permanecer en
    ``https``) y el host contra ``COBRA_HOST_WHITELIST`` antes de realizar la
    siguiente petición. Esto replica la política aplicada en ``corelibs.red``
    para evitar redirecciones abiertas.
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
