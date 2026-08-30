"""Funciones relacionadas con el sistema operativo."""

from __future__ import annotations

import asyncio
import os
import sys
import platform
import shutil
import subprocess
from collections import deque
from collections.abc import Iterable
from typing import Any, AsyncIterator, cast

# Variable de entorno que permite definir una lista blanca mínima
WHITELIST_ENV = "COBRA_EJECUTAR_PERMITIDOS"
# Lista capturada una sola vez al importar el módulo para evitar cambios en
# tiempo de ejecución.
_lista_env = os.getenv(WHITELIST_ENV)
PERMITIDOS_FIJOS = tuple(_lista_env.split(os.pathsep)) if _lista_env else ()
EQUIVALENCIAS_SEMANTICAS_SISTEMA: dict[str, str] = {
    "getcwd": "directorio_actual",
    "getenv": "obtener_entorno",
    "setenv": "definir_entorno",
    "platform.system": "nombre_sistema",
    "platform.machine": "arquitectura",
    "subprocess.run": "ejecutar",
}


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
        raise RuntimeError("No se pudo verificar el ejecutable autorizado") from exc

    if actual.st_dev != st_dev or actual.st_ino != st_ino:
        raise RuntimeError("El ejecutable cambió durante la ejecución")


def _verificar_ruta(exe_real: str, st_dev: int, st_ino: int) -> None:
    try:
        actual = os.stat(exe_real)
    except OSError as exc:
        raise RuntimeError("El ejecutable cambió durante la ejecución") from exc

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
        opciones_descriptor: dict[str, Any] = {}
        if os.name == "posix" and sys.platform.startswith("linux"):
            if not os.path.exists("/proc/self/fd"):
                raise RuntimeError("No está disponible /proc/self/fd")
            args_exec[0] = f"/proc/self/fd/{fd}"
            # pass_fds hace heredable el fd abierto con O_CLOEXEC solo en el hijo.
            opciones_descriptor = {"pass_fds": (fd,), "close_fds": True}

        resultado = subprocess.run(
            args_exec,
            check=True,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=timeout,
            **opciones_descriptor,
        )
        _verificar_descriptor(fd, st_dev, st_ino)
        _verificar_ruta(exe_real, st_dev, st_ino)
        return cast(str, resultado.stdout)
    except subprocess.TimeoutExpired as exc:
        if exc.stderr:
            return exc.stderr
        raise RuntimeError(
            f"Tiempo de espera agotado al ejecutar '{' '.join(args)}'"
        ) from exc
    except subprocess.CalledProcessError as exc:
        if exc.stderr:
            return cast(str, exc.stderr)
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
        opciones_descriptor: dict[str, Any] = {}
        if os.name == "posix" and sys.platform.startswith("linux"):
            if not os.path.exists("/proc/self/fd"):
                raise RuntimeError("No está disponible /proc/self/fd")
            args_exec[0] = f"/proc/self/fd/{fd}"
            # pass_fds hace heredable el fd abierto con O_CLOEXEC solo en el hijo.
            opciones_descriptor = {"pass_fds": (fd,), "close_fds": True}

        proc = await asyncio.create_subprocess_exec(
            *args_exec,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            **opciones_descriptor,
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
    tareas_lectura: list[asyncio.Task[None]] = []
    stderr_chunks: deque[bytes] = deque()
    stderr_tamano = 0
    limite_stderr = 64 * 1024
    bucle = asyncio.get_running_loop()
    deadline = None if timeout is None else bucle.time() + timeout

    async def esperar(esperable: Any) -> Any:
        if deadline is None:
            return await esperable
        restante = deadline - bucle.time()
        if restante <= 0:
            if hasattr(esperable, "close"):
                esperable.close()
            raise asyncio.TimeoutError
        return await asyncio.wait_for(esperable, restante)

    async def drenar_stdout(cola: asyncio.Queue[bytes | None]) -> None:
        assert proc is not None and proc.stdout is not None
        try:
            while chunk := await proc.stdout.readline():
                await cola.put(chunk)
        finally:
            await cola.put(None)

    async def drenar_stderr() -> None:
        nonlocal stderr_tamano
        assert proc is not None and proc.stderr is not None
        while chunk := await proc.stderr.read(8192):
            stderr_chunks.append(chunk)
            stderr_tamano += len(chunk)
            while stderr_tamano > limite_stderr and stderr_chunks:
                exceso = stderr_tamano - limite_stderr
                primero = stderr_chunks[0]
                if len(primero) <= exceso:
                    stderr_tamano -= len(stderr_chunks.popleft())
                else:
                    stderr_chunks[0] = primero[exceso:]
                    stderr_tamano -= exceso

    timeout_error: asyncio.TimeoutError | None = None
    try:
        _verificar_descriptor(fd, st_dev, st_ino)
        _verificar_ruta(exe_real, st_dev, st_ino)
        opciones_descriptor: dict[str, Any] = {}
        if os.name == "posix" and sys.platform.startswith("linux"):
            if not os.path.exists("/proc/self/fd"):
                raise RuntimeError("No está disponible /proc/self/fd")
            args_exec[0] = f"/proc/self/fd/{fd}"
            # pass_fds hace heredable el fd abierto con O_CLOEXEC solo en el hijo.
            opciones_descriptor = {"pass_fds": (fd,), "close_fds": True}
        try:
            proc = await esperar(
                asyncio.create_subprocess_exec(
                    *args_exec,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                    **opciones_descriptor,
                )
            )
            cola_stdout: asyncio.Queue[bytes | None] = asyncio.Queue(maxsize=1)
            tareas_lectura = [
                asyncio.create_task(drenar_stdout(cola_stdout)),
                asyncio.create_task(drenar_stderr()),
            ]
            while (chunk := await esperar(cola_stdout.get())) is not None:
                yield chunk.decode("utf-8", errors="replace")
            await esperar(tareas_lectura[0])
            await esperar(proc.wait())
        except asyncio.TimeoutError as exc:
            timeout_error = exc
    finally:
        try:
            if proc is not None and proc.returncode is None:
                proc.kill()
            if proc is not None:
                await proc.wait()
            for tarea in tareas_lectura:
                if not tarea.done():
                    tarea.cancel()
            if tareas_lectura:
                await asyncio.gather(*tareas_lectura, return_exceptions=True)
            _verificar_descriptor(fd, st_dev, st_ino)
            _verificar_ruta(exe_real, st_dev, st_ino)
        finally:
            try:
                os.close(fd)
            except OSError:
                pass

    stderr_bytes = b"".join(stderr_chunks)
    if timeout_error is not None:
        detalle = _decodificar(stderr_bytes).strip()
        mensaje = f"Tiempo de espera agotado al ejecutar '{' '.join(args)}'"
        if detalle:
            mensaje = f"{mensaje}: {detalle}"
        raise RuntimeError(mensaje) from timeout_error

    if proc is not None and proc.returncode:
        mensaje = f"Error al ejecutar '{' '.join(args)}': código {proc.returncode}"
        if stderr_bytes:
            mensaje = f"{mensaje}: {_decodificar(stderr_bytes)}"
        raise RuntimeError(mensaje)


def obtener_env(nombre: str) -> str | None:
    """Devuelve el valor de una variable de entorno."""
    return os.getenv(nombre)


def listar_dir(ruta: str) -> list[str]:
    """Lista los archivos de un directorio."""
    from pcobra.corelibs.archivo import _resolver_ruta_filesystem_confinado

    objetivo = _resolver_ruta_filesystem_confinado(ruta)
    return os.listdir(objetivo)


def _error_sistema(operacion: str, exc: Exception) -> RuntimeError:
    return RuntimeError(f"Error del sistema en '{operacion}': {exc}")


async def ejecutar_comando_async(
    comando: list[str],
    permitidos: Iterable[str] | None = None,
    timeout: int | float | None = None,
) -> str:
    """Contrato estable en español para ejecutar comandos asíncronos."""
    try:
        return await ejecutar_async(comando, permitidos=permitidos, timeout=timeout)
    except Exception as exc:
        raise _error_sistema("ejecutar_comando_async", exc) from None


def directorio_actual() -> str:
    """Devuelve la ruta del directorio de trabajo actual."""

    return os.getcwd()


__all__ = [
    "obtener_os",
    "ejecutar",
    "ejecutar_async",
    "ejecutar_stream",
    "obtener_env",
    "listar_dir",
    "ejecutar_comando_async",
    "directorio_actual",
]


PUBLIC_API_SISTEMA: tuple[str, ...] = tuple(__all__)


def _validar_superficie_publica_sistema() -> None:
    if tuple(__all__) != PUBLIC_API_SISTEMA:
        raise RuntimeError(
            "[STARTUP CONTRACT] sistema.__all__ debe exponer únicamente la API pública canónica de Cobra."
        )


_validar_superficie_publica_sistema()
