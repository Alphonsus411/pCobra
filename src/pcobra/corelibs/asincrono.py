"""Utilidades asincrónicas de alto nivel para las corrutinas de Cobra."""

from __future__ import annotations

import asyncio
from contextlib import suppress
from typing import Any, Awaitable, Coroutine, TypeVar

T = TypeVar("T")


def _asegurar_tarea(
    awaitable: Awaitable[T] | Coroutine[Any, Any, T]
) -> asyncio.Future[T]:
    """Crea o reutiliza una tarea asociada a ``awaitable``."""

    if isinstance(awaitable, asyncio.Task):
        return awaitable
    if asyncio.isfuture(awaitable):  # pragma: no cover - compatibilidad
        return asyncio.ensure_future(awaitable)
    if not asyncio.iscoroutine(awaitable):
        raise TypeError("Se esperaba una corrutina o tarea de asyncio")
    return asyncio.create_task(awaitable)


async def recolectar(
    *corutinas: Awaitable[Any] | Coroutine[Any, Any, Any],
    return_exceptions: bool = False,
) -> list[Any]:
    """Ejecuta ``corutinas`` en paralelo y devuelve sus resultados.

    Su comportamiento equivale al de :func:`asyncio.gather` y recuerda a
    ``Promise.all`` en JavaScript.
    """

    if not corutinas:
        return []

    tareas = [_asegurar_tarea(corutina) for corutina in corutinas]
    try:
        return await asyncio.gather(*tareas, return_exceptions=return_exceptions)
    except asyncio.CancelledError:
        for tarea in tareas:
            tarea.cancel()
        raise
    except Exception:
        if not return_exceptions:
            for tarea in tareas:
                tarea.cancel()
        raise
    finally:
        await asyncio.gather(*tareas, return_exceptions=True)


async def carrera(
    *corutinas: Awaitable[T] | Coroutine[Any, Any, T]
) -> T:
    """Devuelve el primer resultado disponible entre ``corutinas``.

    Internamente usa :func:`asyncio.wait` con ``FIRST_COMPLETED`` igual que un
    ``Promise.race``.
    """

    if not corutinas:
        raise ValueError("carrera() necesita al menos una corrutina")

    tareas = [_asegurar_tarea(corutina) for corutina in corutinas]
    pendientes: set[asyncio.Future[T]] = set()
    terminadas: set[asyncio.Future[T]] = set()
    ganadora: asyncio.Future[T] | None = None

    try:
        terminadas, pendientes = await asyncio.wait(
            tareas, return_when=asyncio.FIRST_COMPLETED
        )
        if not terminadas:
            raise RuntimeError("Ninguna tarea finalizó")
        ganadora = next(iter(terminadas))
        return await ganadora
    except asyncio.CancelledError:
        for tarea in tareas:
            tarea.cancel()
        raise
    finally:
        for tarea in pendientes:
            tarea.cancel()
        if pendientes:
            await asyncio.gather(*pendientes, return_exceptions=True)
        for tarea in terminadas:
            if tarea is ganadora:
                continue
            with suppress(Exception):
                await tarea


async def esperar_timeout(
    corutina: Awaitable[T] | Coroutine[Any, Any, T], timeout: float | None
) -> T:
    """Espera ``corutina`` hasta ``timeout`` segundos antes de fallar.

    Envoltorio directo sobre :func:`asyncio.wait_for` con manejo explícito de
    cancelaciones.
    """

    tarea = _asegurar_tarea(corutina)
    try:
        return await asyncio.wait_for(tarea, timeout)
    except asyncio.TimeoutError:
        tarea.cancel()
        with suppress(asyncio.CancelledError):
            await tarea
        raise
    except asyncio.CancelledError:
        tarea.cancel()
        with suppress(asyncio.CancelledError):
            await tarea
        raise
    finally:
        if not tarea.done():
            tarea.cancel()
            with suppress(asyncio.CancelledError):
                await tarea


def crear_tarea(
    corutina: Coroutine[Any, Any, T] | Awaitable[T]
) -> asyncio.Task[T]:
    """Envuelve :func:`asyncio.create_task` para integrar corrutinas Cobra."""

    if isinstance(corutina, asyncio.Task):
        return corutina
    if asyncio.isfuture(corutina):  # pragma: no cover - compatibilidad
        return asyncio.ensure_future(corutina)
    if not asyncio.iscoroutine(corutina):
        raise TypeError("crear_tarea() requiere una corrutina de asyncio")
    return asyncio.create_task(corutina)
