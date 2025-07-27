"""Funciones relacionadas con el sistema operativo."""

import os
import platform
import subprocess
from typing import Iterable


def obtener_os() -> str:
    """Retorna el nombre del sistema operativo."""
    return platform.system()


def ejecutar(comando: list[str], permitidos: Iterable[str] | None = None) -> str:
    """Ejecuta un comando y devuelve su salida.

    ``comando`` debe ser una lista de argumentos que se pasa
    directamente a ``subprocess.run`` sin crear un shell.
    Opcionalmente ``permitidos`` define una lista blanca de programas
    autorizados; si se especifica y el primer elemento de ``comando`` no
    está presente se lanza ``ValueError``.

    Si el comando finaliza con un código de error se captura la
    excepción ``subprocess.CalledProcessError`` devolviendo ``stderr``
    cuando esté disponible o lanzando un ``RuntimeError`` con
    información detallada.
    """
    if (
        permitidos is not None
        and comando
        and os.path.basename(comando[0]) not in permitidos
    ):
        raise ValueError(f"Comando no permitido: {comando[0]}")
    args = comando
    try:
        resultado = subprocess.run(
            args,
            check=True,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        return resultado.stdout
    except subprocess.CalledProcessError as exc:
        if exc.stderr:
            return exc.stderr
        raise RuntimeError(f"Error al ejecutar '{' '.join(comando)}': {exc}") from exc


def obtener_env(nombre: str) -> str | None:
    """Devuelve el valor de una variable de entorno."""
    return os.getenv(nombre)


def listar_dir(ruta: str) -> list[str]:
    """Lista los archivos de un directorio."""
    return os.listdir(ruta)
