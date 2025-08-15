"""Funciones relacionadas con el sistema operativo."""

import os
import platform
import shutil
import subprocess
from typing import Iterable


def obtener_os() -> str:
    """Retorna el nombre del sistema operativo."""
    return platform.system()


def ejecutar(comando: list[str], permitidos: Iterable[str] | None = None) -> str:
    """Ejecuta un comando y devuelve su salida.

    ``comando`` debe ser una lista de argumentos que se pasa
    directamente a ``subprocess.run`` sin crear un shell.
    ``permitidos`` es opcional y define una lista blanca de rutas
    absolutas de ejecutables autorizados; si se especifica y la ruta
    real del programa no coincide exactamente con alguna de ellas se
    lanza ``ValueError``.

    Si el comando finaliza con un código de error se captura la
    excepción ``subprocess.CalledProcessError`` devolviendo ``stderr``
    cuando esté disponible o lanzando un ``RuntimeError`` con
    información detallada.
    """
    if permitidos is not None and comando:
        exe = comando[0]
        exe_resuelto = shutil.which(exe) if not os.path.isabs(exe) else exe
        if exe_resuelto is None:
            raise ValueError(f"Comando no permitido: {exe}")
        exe_real = os.path.realpath(exe_resuelto)
        permitidos_reales = {os.path.realpath(p) for p in permitidos}
        if exe_real not in permitidos_reales:
            raise ValueError(f"Comando no permitido: {exe_real}")
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
