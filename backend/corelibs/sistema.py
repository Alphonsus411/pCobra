"""Funciones relacionadas con el sistema operativo."""

import os
import platform
import shlex
import subprocess


def obtener_os() -> str:
    """Retorna el nombre del sistema operativo."""
    return platform.system()


def ejecutar(comando: str) -> str:
    """Ejecuta un comando y devuelve su salida.

    Si el comando finaliza con un código de error se captura la excepción
    ``subprocess.CalledProcessError`` devolviendo ``stderr`` cuando esté
    disponible o lanzando un ``RuntimeError`` con información detallada.
    """
    args = shlex.split(comando)
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
        raise RuntimeError(f"Error al ejecutar '{comando}': {exc}") from exc


def obtener_env(nombre: str) -> str | None:
    """Devuelve el valor de una variable de entorno."""
    return os.getenv(nombre)


def listar_dir(ruta: str) -> list[str]:
    """Lista los archivos de un directorio."""
    return os.listdir(ruta)
