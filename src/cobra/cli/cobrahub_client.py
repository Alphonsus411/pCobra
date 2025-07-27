import os

import requests

from cobra.cli.i18n import _
from cobra.cli.utils.messages import mostrar_error, mostrar_info

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
    except (PermissionError, OSError) as exc:
        mostrar_error(_("Error abriendo módulo: {err}").format(err=exc))
        return False
    except requests.RequestException as exc:
        mostrar_error(_("Error publicando módulo: {err}").format(err=exc))
        return False


def descargar_modulo(nombre: str, destino: str) -> bool:
    """Descarga un módulo de CobraHub y lo guarda en ``destino``.

    ``destino`` debe ser una ruta relativa dentro del directorio actual.
    Las rutas absolutas o que contengan ``..`` serán rechazadas.
    """
    if os.path.isabs(destino) or ".." in os.path.normpath(destino).split(os.sep):
        mostrar_error(_("Ruta de destino inválida"))
        return False
    destino_abs = os.path.abspath(destino)
    if not destino_abs.startswith(os.path.abspath(os.getcwd()) + os.sep):
        mostrar_error(_("Ruta de destino inválida"))
        return False
    if not _validar_url():
        return False
    try:
        response = requests.get(
            f"{COBRAHUB_URL}/modulos/{nombre}",
            timeout=5,
        )
        response.raise_for_status()
        try:
            with open(destino_abs, "wb") as f:
                f.write(response.content)
        except (PermissionError, OSError) as exc:
            mostrar_error(_("Error guardando módulo: {err}").format(err=exc))
            return False
        mostrar_info(_("Módulo descargado en {dest}").format(dest=destino_abs))
        return True
    except requests.RequestException as exc:
        mostrar_error(_("Error descargando módulo: {err}").format(err=exc))
        return False
