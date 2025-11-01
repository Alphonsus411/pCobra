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
) -> tuple[list[str], str, int, int, int]:
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

    flags = os.O_RDONLY
    if hasattr(os, "O_CLOEXEC"):
        flags |= os.O_CLOEXEC

    fd = -1
    try:
        fd = os.open(exe_real, flags)
        stat_info = os.fstat(fd)
    except OSError:
        if fd >= 0:
            os.close(fd)
        raise

    args[0] = exe_real
    return args, exe_real, fd, stat_info.st_dev, stat_info.st_ino


def _verificar_descriptor(fd: int, st_dev: int, st_ino: int) -> None:
    try:
        actual = os.fstat(fd)
    except OSError as exc:
        raise RuntimeError(
            "No se pudo verificar el ejecutable autorizado"
        ) from exc

    if actual.st_dev != st_dev or actual.st_ino != st_ino:
        raise RuntimeError("El ejecutable cambió durante la ejecución")


def _verificar_ruta(exe_real: str, st_dev: int, st_ino: int) -> None:
    try:
        actual = os.stat(exe_real)
    except OSError as exc:
        raise RuntimeError(
            "El ejecutable cambió durante la ejecución"
        ) from exc

    if actual.st_dev != st_dev or actual.st_ino != st_ino:
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
    (TOCTOU), el ejecutable autorizado se abre con ``os.open`` y se
    ejecuta a través del descriptor asociado cuando la plataforma lo
    permite. Antes y después de la invocación se validan ``st_dev`` y
    ``st_ino`` utilizando ``os.fstat`` para confirmar que el descriptor
    sigue apuntando al binario autorizado y se compara el estado actual
    del archivo con ``os.stat`` para abortar si la ruta fue sustituida.
    """
    args, exe_real, fd, st_dev, st_ino = _resolver_ejecutable(comando, permitidos)
    args_exec = list(args)
    try:
        _verificar_descriptor(fd, st_dev, st_ino)
        _verificar_ruta(exe_real, st_dev, st_ino)
        if os.name == "posix":
            args_exec[0] = f"/proc/self/fd/{fd}"

        resultado = subprocess.run(
            args_exec,
            check=True,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=timeout,
        )
        _verificar_descriptor(fd, st_dev, st_ino)
        _verificar_ruta(exe_real, st_dev, st_ino)
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
    finally:
        try:
            os.close(fd)
        except OSError:
            pass


def _decodificar(data: bytes | None) -> str:
    return (data or b"").decode("utf-8", errors="replace")


async def ejecutar_async(
    comando: list[str],
    permitidos: Iterable[str] | None = None,
    timeout: int | float | None = None,
) -> str:
    """Versión asíncrona de :func:`ejecutar`."""

    args, exe_real, fd, st_dev, st_ino = _resolver_ejecutable(comando, permitidos)
    args_exec = list(args)
    proc: asyncio.subprocess.Process | None = None
    try:
        _verificar_descriptor(fd, st_dev, st_ino)
        _verificar_ruta(exe_real, st_dev, st_ino)
        if os.name == "posix":
            args_exec[0] = f"/proc/self/fd/{fd}"

        proc = await asyncio.create_subprocess_exec(
            *args_exec,
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

        _verificar_descriptor(fd, st_dev, st_ino)
        _verificar_ruta(exe_real, st_dev, st_ino)
        if proc.returncode:
            if stderr_bytes:
                return _decodificar(stderr_bytes)
            raise RuntimeError(
                f"Error al ejecutar '{' '.join(args)}': código {proc.returncode}"
            )
        return _decodificar(stdout_bytes)
    finally:
        try:
            os.close(fd)
        except OSError:
            pass


async def ejecutar_stream(
    comando: list[str],
    permitidos: Iterable[str] | None = None,
    timeout: int | float | None = None,
) -> AsyncIterator[str]:
    """Devuelve un iterador asíncrono con la salida estándar del proceso."""

    args, exe_real, fd, st_dev, st_ino = _resolver_ejecutable(comando, permitidos)
    args_exec = list(args)
    proc: asyncio.subprocess.Process | None = None
    stderr_bytes = b""
    try:
        _verificar_descriptor(fd, st_dev, st_ino)
        _verificar_ruta(exe_real, st_dev, st_ino)
        if os.name == "posix":
            args_exec[0] = f"/proc/self/fd/{fd}"
        proc = await asyncio.create_subprocess_exec(
            *args_exec,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        loop = asyncio.get_running_loop()
        inicio = loop.time()
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
        _verificar_descriptor(fd, st_dev, st_ino)
        _verificar_ruta(exe_real, st_dev, st_ino)
        try:
            os.close(fd)
        except OSError:
            pass

    if proc is not None and proc.returncode:
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
