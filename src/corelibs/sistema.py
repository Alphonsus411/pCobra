"""Funciones relacionadas con el sistema operativo."""

import os
import platform
import shutil
import subprocess
from typing import Iterable

# Variable de entorno que permite definir una lista blanca mínima
WHITELIST_ENV = "COBRA_EJECUTAR_PERMITIDOS"
# Lista capturada una sola vez al importar el módulo para evitar cambios en
# tiempo de ejecución.
_lista_env = os.getenv(WHITELIST_ENV)
PERMITIDOS_FIJOS = (
    tuple(_lista_env.split(os.pathsep)) if _lista_env else ()
)


def obtener_os() -> str:
    """Retorna el nombre del sistema operativo."""
    return platform.system()


def ejecutar(
    comando: list[str],
    permitidos: Iterable[str] | None = None,
    timeout: int | float | None = None,
) -> str:
    """Ejecuta un comando y devuelve su salida.

    ``comando`` debe ser una lista no vacía de argumentos que se pasa
    directamente a ``subprocess.run`` sin crear un shell. Se lanza
    ``ValueError`` si la lista está vacía. ``permitidos`` define una lista blanca de rutas absolutas de ejecutables
    autorizados; este parámetro es obligatorio. Si se invoca la función
    sin una lista se utilizará la capturada desde
    ``COBRA_EJECUTAR_PERMITIDOS`` al importar el módulo, siempre que no
    esté vacía. Los cambios posteriores en la variable de entorno no
    surten efecto.

    ``timeout`` especifica el tiempo máximo de espera en segundos. Si se
    excede este límite se captura ``subprocess.TimeoutExpired``
    devolviendo ``stderr`` cuando esté disponible o lanzando un
    ``RuntimeError`` descriptivo. Por defecto no hay límite.

    Si el comando finaliza con un código de error se captura la
    excepción ``subprocess.CalledProcessError`` devolviendo ``stderr``
    cuando esté disponible o lanzando un ``RuntimeError`` con
    información detallada.
    """
    if not comando:
        raise ValueError("Comando vacío")

    if permitidos is None:
        if PERMITIDOS_FIJOS:
            permitidos = PERMITIDOS_FIJOS
        else:
            raise ValueError("Se requiere lista blanca de comandos permitidos")

    if comando:
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
            timeout=timeout,
        )
        return resultado.stdout
    except subprocess.TimeoutExpired as exc:
        if exc.stderr:
            return exc.stderr
        raise RuntimeError(
            f"Tiempo de espera agotado al ejecutar '{' '.join(comando)}'"
        ) from exc
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
