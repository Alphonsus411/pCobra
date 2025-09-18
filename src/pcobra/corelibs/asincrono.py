"""Utilidades asincrónicas de alto nivel para las corrutinas de Cobra."""

from __future__ import annotations

import asyncio
from contextlib import suppress
from typing import Any, AsyncIterator, Awaitable, Callable, Coroutine, Iterable, TypeVar

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


async def primero_exitoso(
    *corutinas: Awaitable[T] | Coroutine[Any, Any, T]
) -> T:
    """Devuelve el primer resultado satisfactorio de ``corutinas``.

    Opera de manera análoga a ``Promise.any`` en JavaScript: se ejecutan todas
    las corrutinas en paralelo y se devuelve el primer valor que no levante
    excepciones. Si todas fallan se lanza una :class:`ExceptionGroup` con los
    errores encontrados. Una cancelación externa provoca que el resto de tareas
    se cancelen y se propague el :class:`asyncio.CancelledError` original.
    """

    if not corutinas:
        raise ValueError("primero_exitoso() necesita al menos una corrutina")

    tareas = [_asegurar_tarea(corutina) for corutina in corutinas]
    errores: list[BaseException] = []

    try:
        for futura in asyncio.as_completed(tareas):
            try:
                resultado = await futura
            except asyncio.CancelledError:
                for tarea in tareas:
                    tarea.cancel()
                raise
            except BaseException as exc:
                errores.append(exc)
            else:
                for tarea in tareas:
                    if tarea is not futura and not tarea.done():
                        tarea.cancel()
                return resultado
    except asyncio.CancelledError:
        for tarea in tareas:
            tarea.cancel()
        raise
    finally:
        if tareas:
            await asyncio.gather(*tareas, return_exceptions=True)

    if errores:
        raise ExceptionGroup("Todas las tareas fallaron", errores)
    raise RuntimeError("No se obtuvo ningún resultado exitoso")


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


async def iterar_completadas(
    *corutinas: Awaitable[T] | Coroutine[Any, Any, T]
) -> AsyncIterator[T]:
    """Devuelve los resultados a medida que cada corrutina termina.

    Se apoya en :func:`asyncio.as_completed` para ofrecer un comportamiento
    parecido al de ``Promise.any``/``Promise.race`` iterados manualmente en
    JavaScript. Los resultados se emiten en el orden en el que finalizan las
    tareas subyacentes.
    """

    if not corutinas:
        return

    tareas = [_asegurar_tarea(corutina) for corutina in corutinas]
    try:
        for futura in asyncio.as_completed(tareas):
            try:
                resultado = await futura
            except asyncio.CancelledError:
                for tarea in tareas:
                    if tarea is not futura:
                        tarea.cancel()
                raise
            except Exception:
                for tarea in tareas:
                    if tarea is not futura:
                        tarea.cancel()
                raise
            else:
                yield resultado
    except asyncio.CancelledError:
        for tarea in tareas:
            tarea.cancel()
        raise
    finally:
        for tarea in tareas:
            if not tarea.done():
                tarea.cancel()
        if tareas:
            await asyncio.gather(*tareas, return_exceptions=True)


async def mapear_concurrencia(
    funciones: Iterable[Callable[[], Awaitable[T] | Coroutine[Any, Any, T]]],
    limite: int,
    *,
    return_exceptions: bool = False,
) -> list[T | BaseException]:
    """Ejecuta ``funciones`` respetando ``limite`` tareas simultáneas.

    Aplica un control explícito de concurrencia similar a los *worker pools* de
    Go mediante :class:`asyncio.Semaphore`. Al igual que ``Promise.all`` se
    preserva el orden de los resultados, pero es posible limitar cuántas
    corrutinas corren a la vez. Cuando ``return_exceptions`` es ``False`` el
    primer error detiene el resto de tareas; si vale ``True`` las excepciones se
    devuelven en la posición que les corresponde. ``limite`` debe ser al menos
    ``1``.
    """

    if limite < 1:
        raise ValueError("limite debe ser un entero positivo")

    lista_funciones = list(funciones)
    if not lista_funciones:
        return []

    semaforo = asyncio.Semaphore(limite)

    async def ejecutar(funcion: Callable[[], Awaitable[T] | Coroutine[Any, Any, T]]):
        async with semaforo:
            try:
                awaitable = funcion()
            except Exception as exc:
                if isinstance(exc, asyncio.CancelledError):
                    raise
                if return_exceptions:
                    return exc
                raise

            tarea = _asegurar_tarea(awaitable)

            try:
                return await tarea
            except asyncio.CancelledError:
                raise
            except Exception as exc:
                if return_exceptions:
                    return exc
                raise

    tareas = [asyncio.create_task(ejecutar(funcion)) for funcion in lista_funciones]

    try:
        resultados = await asyncio.gather(*tareas, return_exceptions=return_exceptions)
    except asyncio.CancelledError:
        for tarea in tareas:
            tarea.cancel()
        raise
    finally:
        await asyncio.gather(*tareas, return_exceptions=True)

    return list(resultados)


async def recolectar_resultados(
    *corutinas: Awaitable[T] | Coroutine[Any, Any, T]
) -> list[dict[str, Any]]:
    """Ejecuta ``corutinas`` y reporta sus estados finales.

    La forma de la respuesta imita a ``Promise.allSettled`` en JavaScript al
    producir una lista de diccionarios con las claves ``estado``, ``resultado``
    y ``excepcion``. El orden del resultado se mantiene respecto a los
    parámetros proporcionados.
    """

    if not corutinas:
        return []

    tareas = [_asegurar_tarea(corutina) for corutina in corutinas]
    estados: list[dict[str, Any]] = [{} for _ in tareas]

    try:
        for indice, tarea in enumerate(tareas):
            try:
                valor = await tarea
            except asyncio.CancelledError as exc:
                estados[indice] = {
                    "estado": "cancelada",
                    "resultado": None,
                    "excepcion": exc,
                }
            except Exception as exc:
                estados[indice] = {
                    "estado": "rechazada",
                    "resultado": None,
                    "excepcion": exc,
                }
            else:
                estados[indice] = {
                    "estado": "cumplida",
                    "resultado": valor,
                    "excepcion": None,
                }
        return estados
    except asyncio.CancelledError:
        for tarea in tareas:
            tarea.cancel()
        raise
    finally:
        await asyncio.gather(*tareas, return_exceptions=True)
