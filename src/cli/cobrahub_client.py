import os

import requests

from src.cli.i18n import _
from src.cli.utils.messages import mostrar_error, mostrar_info

COBRAHUB_URL = os.environ.get("COBRAHUB_URL", "https://cobrahub.example.com/api")


def _validar_url() -> bool:
    """Verifica que la URL de CobraHub sea segura."""
    if not COBRAHUB_URL.startswith("https://"):
        mostrar_error(_("COBRAHUB_URL debe empezar con https://"))
        return False
    return True


def publicar_modulo(ruta: str) -> bool:
    """Publica un archivo .co en CobraHub."""
    if not _validar_url():
        return False
    if not os.path.exists(ruta):
        mostrar_error(_("No se encontró el módulo {path}").format(path=ruta))
        return False
    try:
        with open(ruta, "rb") as f:
            response = requests.post(
                f"{COBRAHUB_URL}/modulos",
                files={"file": f},
                timeout=5,
            )
        response.raise_for_status()
        mostrar_info(_("Módulo publicado correctamente"))
        return True
    except requests.RequestException as exc:
        mostrar_error(_("Error publicando módulo: {err}").format(err=exc))
        return False


def descargar_modulo(nombre: str, destino: str) -> bool:
    """Descarga un módulo de CobraHub y lo guarda en destino."""
    if not _validar_url():
        return False
    try:
        response = requests.get(
            f"{COBRAHUB_URL}/modulos/{nombre}",
            timeout=5,
        )
        response.raise_for_status()
        with open(destino, "wb") as f:
            f.write(response.content)
        mostrar_info(_("Módulo descargado en {dest}").format(dest=destino))
        return True
    except requests.RequestException as exc:
        mostrar_error(_("Error descargando módulo: {err}").format(err=exc))
        return False
