"""Funciones relacionadas con el sistema operativo."""

from __future__ import annotations

import asyncio
import os
import platform
import shutil
import subprocess
from collections.abc import Iterable
from typing import AsyncIterator

# Variable de entorno que permite definir una lista blanca mínima
WHITELIST_ENV = "COBRA_EJECUTAR_PERMITIDOS"
# Lista capturada una sola vez al importar el módulo para evitar cambios en
# tiempo de ejecución.
_lista_env = os.getenv(WHITELIST_ENV)
PERMITIDOS_FIJOS = tuple(_lista_env.split(os.pathsep)) if _lista_env else ()


def _normalizar_rutas(rutas: Iterable[str]) -> set[str]:
    return {
        os.path.normcase(os.path.normpath(os.path.realpath(ruta))) for ruta in rutas
    }


def _obtener_permitidos(permitidos: Iterable[str] | None) -> set[str]:
    if permitidos is None:
        if PERMITIDOS_FIJOS:
            permitidos_iter = PERMITIDOS_FIJOS
        else:
            raise ValueError("Se requiere lista blanca de comandos permitidos")
    else:
        permitidos_iter = permitidos
    normalizados = _normalizar_rutas(permitidos_iter)
    if not normalizados:
        raise ValueError("Lista blanca de comandos vacía")
    return normalizados


def _resolver_ejecutable(
    comando: list[str], permitidos: Iterable[str] | None
) -> tuple[list[str], str, int]:
    if not comando:
        raise ValueError("Comando vacío")

    args = list(comando)

    permitidos_reales = _obtener_permitidos(permitidos)

    exe = args[0]
    exe_resuelto = shutil.which(exe) if not os.path.isabs(exe) else exe
    if exe_resuelto is None:
        raise ValueError(f"Comando no permitido: {exe}")
    exe_real = os.path.realpath(exe_resuelto)
    exe_normalizado = os.path.normcase(os.path.normpath(exe_real))
    if exe_normalizado not in permitidos_reales:
        raise ValueError(f"Comando no permitido: {exe_real}")
    inode = os.stat(exe_real).st_ino
    args[0] = exe_real
    return args, exe_real, inode


def _verificar_inode(exe_real: str, inode_inicial: int) -> None:
    inode_final = os.stat(exe_real).st_ino
    if inode_final != inode_inicial:
        raise RuntimeError("El ejecutable cambió durante la ejecución")


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
    ``ValueError`` si la lista está vacía. ``permitidos`` define una lista
    blanca de rutas absolutas de ejecutables autorizados; este parámetro es
    obligatorio. Las rutas suministradas deben estar normalizadas previamente
    con ``os.path.normpath`` y ``os.path.normcase`` para asegurar
    comparaciones coherentes en plataformas con distinta sensibilidad a las
    mayúsculas. Si se invoca la función
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

    Para mitigar ataques de tiempo de comprobación a tiempo de uso
    (TOCTOU), se registra el ``inode`` del ejecutable antes de la
    ejecución y se vuelve a comprobar después de llamar a
    ``subprocess.run``. Si el ``inode`` difiere, se lanza un
    ``RuntimeError`` indicando que el archivo fue modificado durante el
    proceso.
    """
    args, exe_real, inode = _resolver_ejecutable(comando, permitidos)
    try:
        resultado = subprocess.run(
            args,
            check=True,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=timeout,
        )
        _verificar_inode(exe_real, inode)
        return resultado.stdout
    except subprocess.TimeoutExpired as exc:
        if exc.stderr:
            return exc.stderr
        raise RuntimeError(
            f"Tiempo de espera agotado al ejecutar '{' '.join(args)}'"
        ) from exc
    except subprocess.CalledProcessError as exc:
        if exc.stderr:
            return exc.stderr
        raise RuntimeError(f"Error al ejecutar '{' '.join(args)}': {exc}") from exc


def _decodificar(data: bytes | None) -> str:
    return (data or b"").decode("utf-8", errors="replace")


async def ejecutar_async(
    comando: list[str],
    permitidos: Iterable[str] | None = None,
    timeout: int | float | None = None,
) -> str:
    """Versión asíncrona de :func:`ejecutar`."""

    args, exe_real, inode = _resolver_ejecutable(comando, permitidos)
    proc = await asyncio.create_subprocess_exec(
        *args,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    try:
        stdout_bytes, stderr_bytes = await asyncio.wait_for(
            proc.communicate(), timeout=timeout
        )
    except asyncio.TimeoutError as exc:
        proc.kill()
        stdout_bytes, stderr_bytes = await proc.communicate()
        if stderr_bytes:
            return _decodificar(stderr_bytes)
        raise RuntimeError(
            f"Tiempo de espera agotado al ejecutar '{' '.join(args)}'"
        ) from exc
    _verificar_inode(exe_real, inode)
    if proc.returncode:
        if stderr_bytes:
            return _decodificar(stderr_bytes)
        raise RuntimeError(
            f"Error al ejecutar '{' '.join(args)}': código {proc.returncode}"
        )
    return _decodificar(stdout_bytes)


async def ejecutar_stream(
    comando: list[str],
    permitidos: Iterable[str] | None = None,
    timeout: int | float | None = None,
) -> AsyncIterator[str]:
    """Devuelve un iterador asíncrono con la salida estándar del proceso."""

    args, exe_real, inode = _resolver_ejecutable(comando, permitidos)
    proc = await asyncio.create_subprocess_exec(
        *args,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    loop = asyncio.get_running_loop()
    inicio = loop.time()
    stderr_bytes = b""
    try:
        assert proc.stdout is not None
        while True:
            restante = None
            if timeout is not None:
                restante = timeout - (loop.time() - inicio)
                if restante <= 0:
                    raise asyncio.TimeoutError
            try:
                if restante is None:
                    chunk = await proc.stdout.readline()
                else:
                    chunk = await asyncio.wait_for(proc.stdout.readline(), restante)
            except asyncio.TimeoutError as exc:
                proc.kill()
                _, stderr_bytes = await proc.communicate()
                if stderr_bytes:
                    raise RuntimeError(_decodificar(stderr_bytes)) from exc
                raise RuntimeError(
                    f"Tiempo de espera agotado al ejecutar '{' '.join(args)}'"
                ) from exc
            if not chunk:
                break
            yield chunk.decode("utf-8", errors="replace")

        restante = None
        if timeout is not None:
            restante = timeout - (loop.time() - inicio)
            if restante <= 0:
                raise asyncio.TimeoutError
        try:
            if restante is None:
                await proc.wait()
            else:
                await asyncio.wait_for(proc.wait(), restante)
        except asyncio.TimeoutError as exc:
            proc.kill()
            _, stderr_bytes = await proc.communicate()
            if stderr_bytes:
                raise RuntimeError(_decodificar(stderr_bytes)) from exc
            raise RuntimeError(
                f"Tiempo de espera agotado al ejecutar '{' '.join(args)}'"
            ) from exc

        if proc.stderr is not None:
            stderr_bytes = await proc.stderr.read()
    finally:
        _verificar_inode(exe_real, inode)

    if proc.returncode:
        if stderr_bytes:
            raise RuntimeError(_decodificar(stderr_bytes))
        raise RuntimeError(
            f"Error al ejecutar '{' '.join(args)}': código {proc.returncode}"
        )


def obtener_env(nombre: str) -> str | None:
    """Devuelve el valor de una variable de entorno."""
    return os.getenv(nombre)


def listar_dir(ruta: str) -> list[str]:
    """Lista los archivos de un directorio."""
    return os.listdir(ruta)
