"""Utilidades asincrónicas de alto nivel para las corrutinas de Cobra."""

from __future__ import annotations

import asyncio
import random
from contextlib import asynccontextmanager, suppress
import functools
from typing import (
    TYPE_CHECKING,
    Any,
    AsyncIterator,
    Awaitable,
    Callable,
    Coroutine,
    Iterable,
    Sequence,
    TypeVar,
)

T = TypeVar("T")

try:  # pragma: no cover - Python >= 3.11 lo define de forma nativa
    ExceptionGroup
except NameError:  # pragma: no cover - compatibilidad para Python < 3.11
    class ExceptionGroup(Exception):
        """Implementación mínima para entornos sin ``ExceptionGroup``."""

        def __init__(self, mensaje: str, excepciones: Iterable[BaseException]):
            super().__init__(mensaje)
            self.exceptions = list(excepciones)


if TYPE_CHECKING:  # pragma: no cover - solo para tipado
    from typing import Protocol

    class _TaskGroupProtocol(Protocol):
        def create_task(
            self, corutina: Coroutine[Any, Any, Any], *, name: str | None = ...
        ) -> asyncio.Task[Any]:
            ...



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


def proteger_tarea(
    awaitable: Awaitable[T] | Coroutine[Any, Any, T]
) -> asyncio.Future[T]:
    """Impide que las cancelaciones externas afecten a ``awaitable``."""

    tarea = _asegurar_tarea(awaitable)
    return asyncio.shield(tarea)


@asynccontextmanager
async def limitar_tiempo(
    segundos: float | None, *, mensaje: str | None = None
) -> AsyncIterator[None]:
    """Limita el tiempo de ejecución del bloque asíncrono."""

    if segundos is None:
        yield
        return

    timeout_cm = getattr(asyncio, "timeout", None)
    if timeout_cm is not None:
        try:
            async with timeout_cm(segundos):
                yield
        except asyncio.TimeoutError:
            if mensaje is not None:
                raise asyncio.TimeoutError(mensaje) from None
            raise
        return

    loop = asyncio.get_running_loop()
    tarea_actual = asyncio.current_task()
    if tarea_actual is None:  # pragma: no cover - entornos ajenos a asyncio
        yield
        return

    fin = loop.create_future()
    expirado = False

    async def vigilante() -> None:
        nonlocal expirado
        try:
            await asyncio.wait_for(fin, segundos)
        except asyncio.TimeoutError:
            expirado = True
            tarea_actual.cancel()
            raise

    supervisor = asyncio.create_task(vigilante())
    try:
        try:
            yield
        except asyncio.CancelledError:
            if expirado:
                if mensaje is not None:
                    raise asyncio.TimeoutError(mensaje) from None
                raise asyncio.TimeoutError() from None
            raise
    finally:
        if not fin.done():
            fin.set_result(None)
        with suppress(asyncio.CancelledError):
            try:
                await supervisor
            except asyncio.TimeoutError:
                if not expirado:
                    raise


async def ejecutar_en_hilo(
    funcion: Callable[..., T], *args: Any, **kwargs: Any
) -> T:
    """Ejecuta ``funcion`` en un hilo auxiliar respetando la interfaz de asyncio."""

    if not callable(funcion):
        raise TypeError("ejecutar_en_hilo() requiere un callable")

    to_thread = getattr(asyncio, "to_thread", None)
    if to_thread is not None:
        return await to_thread(funcion, *args, **kwargs)

    loop = asyncio.get_running_loop()
    if kwargs:
        parcial = functools.partial(funcion, *args, **kwargs)
        return await loop.run_in_executor(None, parcial)
    return await loop.run_in_executor(None, funcion, *args)


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


async def reintentar_async(
    funcion: Callable[[], Awaitable[T] | Coroutine[Any, Any, T]],
    *,
    intentos: int = 3,
    excepciones: type[BaseException]
    | Sequence[type[BaseException]] = (Exception,),
    retardo_inicial: float = 0.1,
    factor_backoff: float = 2.0,
    max_retardo: float | None = None,
    jitter: Callable[[float], float]
    | tuple[float, float]
    | float
    | bool
    | None = None,
) -> T:
    """Ejecuta ``funcion`` reintentando ante errores con *backoff* exponencial.

    Cada vez que ``funcion`` arroja una de las ``excepciones`` controladas se
    reintenta hasta ``intentos`` ocasiones como hace ``Promise.retry`` en
    JavaScript o los lazos de reintento clásicos en Go. Entre intentos se espera
    un retardo exponencial calculado a partir de ``retardo_inicial`` y
    ``factor_backoff``. ``jitter`` permite añadir aleatoriedad para evitar
    congestión masiva en sistemas distribuidos.
    """

    if intentos < 1:
        raise ValueError("intentos debe ser un entero positivo")
    if retardo_inicial < 0:
        raise ValueError("retardo_inicial no puede ser negativo")
    if factor_backoff <= 0:
        raise ValueError("factor_backoff debe ser mayor que cero")
    if max_retardo is not None and max_retardo < 0:
        raise ValueError("max_retardo no puede ser negativo")

    if isinstance(excepciones, type):
        tipos_controlados: tuple[type[BaseException], ...] = (excepciones,)
    else:
        tipos_controlados = tuple(excepciones)

    if not tipos_controlados:
        raise ValueError("excepciones no puede estar vacío")

    for tipo in tipos_controlados:
        if not isinstance(tipo, type) or not issubclass(tipo, BaseException):
            raise TypeError("Cada entrada de excepciones debe ser una excepción")

    def _aplicar_jitter(valor: float) -> float:
        if jitter is None:
            return valor
        if callable(jitter):
            ajustado = jitter(valor)
        elif isinstance(jitter, bool):
            if not jitter:
                return valor
            ajustado = random.uniform(0.0, valor)
        elif isinstance(jitter, tuple):
            if len(jitter) != 2:
                raise ValueError("jitter como tupla debe tener dos elementos")
            minimo, maximo = (float(jitter[0]), float(jitter[1]))
            if minimo > maximo:
                minimo, maximo = maximo, minimo
            ajustado = random.uniform(minimo, maximo)
        else:
            amplitud = float(jitter)
            minimo = valor - amplitud
            maximo = valor + amplitud
            if minimo > maximo:
                minimo, maximo = maximo, minimo
            ajustado = random.uniform(minimo, maximo)
        return max(0.0, float(ajustado))

    def _calcular_espera(intento_actual: int) -> float:
        espera = retardo_inicial * (factor_backoff ** (intento_actual - 1))
        if max_retardo is not None:
            espera = min(espera, max_retardo)
        if espera <= 0:
            return 0.0
        return _aplicar_jitter(espera)

    ultimo_error: BaseException | None = None

    for numero_intento in range(1, intentos + 1):
        try:
            awaitable = funcion()
        except tipos_controlados as exc:
            if isinstance(exc, asyncio.CancelledError):
                raise
            ultimo_error = exc
        else:
            tarea = _asegurar_tarea(awaitable)
            try:
                return await tarea
            except tipos_controlados as exc:
                if isinstance(exc, asyncio.CancelledError):
                    raise
                ultimo_error = exc
            except asyncio.CancelledError:
                raise

        if numero_intento == intentos:
            assert ultimo_error is not None
            raise ultimo_error

        espera = _calcular_espera(numero_intento)
        if espera > 0:
            await asyncio.sleep(espera)

    if ultimo_error is not None:  # pragma: no cover - ruta por sanidad
        raise ultimo_error
    raise RuntimeError("reintentar_async terminó sin resultado ni error")


@asynccontextmanager
async def grupo_tareas() -> AsyncIterator["_TaskGroupProtocol"]:
    """Gestiona un grupo de tareas que se cancelan juntas ante errores.

    El manejador aprovecha :class:`asyncio.TaskGroup` en Python 3.11+ y ofrece
    una implementación compatible para versiones anteriores. Todas las tareas
    lanzadas mediante ``create_task`` se esperan al abandonar el contexto y,
    cuando alguna falla, el resto se cancela propagando un
    :class:`ExceptionGroup` con los errores capturados.
    """

    if hasattr(asyncio, "TaskGroup"):
        async with asyncio.TaskGroup() as grupo_real:
            yield grupo_real
        return

    tareas: set[asyncio.Task[Any]] = set()

    class _GrupoCompat:
        def create_task(
            self, corutina: Coroutine[Any, Any, Any], *, name: str | None = None
        ) -> asyncio.Task[Any]:
            if not asyncio.iscoroutine(corutina):
                raise TypeError("grupo_tareas.create_task requiere una corrutina")
            tarea = (
                asyncio.create_task(corutina, name=name)
                if name is not None
                else asyncio.create_task(corutina)
            )
            tareas.add(tarea)
            tarea.add_done_callback(tareas.discard)
            return tarea

    async def _esperar_finalizacion(
        cancelar: bool = False,
    ) -> tuple[list[BaseException], list[BaseException]]:
        pendientes = set(tareas)
        errores: list[BaseException] = []
        cancelaciones: list[BaseException] = []

        if not pendientes:
            return errores, cancelaciones

        if cancelar:
            for tarea in pendientes:
                tarea.cancel()
            modo = asyncio.ALL_COMPLETED
        else:
            modo = asyncio.FIRST_EXCEPTION

        while pendientes:
            terminadas, pendientes = await asyncio.wait(
                pendientes, return_when=modo
            )
            for tarea in terminadas:
                try:
                    await tarea
                except asyncio.CancelledError as exc_cancel:
                    cancelaciones.append(exc_cancel)
                except BaseException as exc_error:
                    errores.append(exc_error)

            if pendientes:
                if cancelar or errores:
                    for tarea in pendientes:
                        tarea.cancel()
                    modo = asyncio.ALL_COMPLETED
                else:
                    modo = asyncio.FIRST_EXCEPTION

        return errores, cancelaciones

    grupo = _GrupoCompat()
    try:
        yield grupo
        errores, _ = await _esperar_finalizacion()
        if errores:
            raise ExceptionGroup("Errores en grupo de tareas", errores) from None
    except asyncio.CancelledError:
        await _esperar_finalizacion(cancelar=True)
        raise
    except BaseException as exc:
        errores, cancelaciones = await _esperar_finalizacion(cancelar=True)
        if errores:
            raise ExceptionGroup("Errores en grupo de tareas", [exc, *errores]) from None
        if cancelaciones:
            raise ExceptionGroup(
                "Errores en grupo de tareas", [exc, *cancelaciones]
            ) from None
        raise
    finally:
        tareas.clear()


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
