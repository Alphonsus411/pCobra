"""Herramientas asincrónicas expuestas en la biblioteca estándar."""

from __future__ import annotations

from typing import (
    Any,
    AsyncContextManager,
    Awaitable,
    Callable,
    Coroutine,
    Sequence,
    TypeVar,
)

from pcobra.corelibs import (
    grupo_tareas as _grupo_tareas,
    proteger_tarea as _proteger_tarea,
    ejecutar_en_hilo as _ejecutar_en_hilo,
    reintentar_async as _reintentar_async,
)

T = TypeVar("T")

__all__ = ["grupo_tareas", "proteger_tarea", "ejecutar_en_hilo", "reintentar_async"]


def grupo_tareas() -> AsyncContextManager[Any]:
    """Crea un grupo de tareas que replica la semántica de ``asyncio.TaskGroup``.

    Este envoltorio delega en :func:`pcobra.corelibs.grupo_tareas` para ofrecer un
    administrador que espera a que todas las tareas finalicen y cancela las
    pendientes cuando se produce un error. Resulta útil para escribir código Cobra
    que requiera coordinar corrutinas en Python 3.10 o versiones anteriores donde
    ``asyncio.TaskGroup`` todavía no existe.
    """

    return _grupo_tareas()


def proteger_tarea(awaitable: Awaitable[T] | Coroutine[Any, Any, T]):
    """Aísla ``awaitable`` de cancelaciones externas al estilo ``Promise.resolve``.

    Igual que ``Promise.resolve`` convierte cualquier valor en una promesa que puede
    esperarse con seguridad, este helper delega en :func:`asyncio.shield` para
    devolver un *future* independiente. De esta forma se evita que una cancelación
    sobre la tarea actual invalide el trabajo original.
    """

    return _proteger_tarea(awaitable)


async def ejecutar_en_hilo(funcion: Callable[..., T], *args: Any, **kwargs: Any) -> T:
    """Ejecuta ``funcion`` en un hilo, similar a resolver tareas con ``Promise``.

    Internamente invoca :func:`asyncio.to_thread` (o su degradación a
    ``loop.run_in_executor``) para integrar código síncrono dentro de pipelines
    asíncronos Cobra. El comportamiento recuerda a ``Promise.resolve`` cuando se
    envuelven operaciones bloqueantes y se espera su resultado en JavaScript.
    """

    return await _ejecutar_en_hilo(funcion, *args, **kwargs)


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
    """Reintenta ``funcion`` aplicando un *backoff* exponencial con *jitter* opcional.

    Envuelve :func:`pcobra.corelibs.reintentar_async` para acercar un patrón
    equivalente al de ``Promise`` en bibliotecas de JavaScript o los bucles de
    reintento habituales con gorutinas en Go. Resulta útil cuando se esperan
    fallos transitorios y se desea espaciar los intentos para aliviar la carga.
    """

    return await _reintentar_async(
        funcion,
        intentos=intentos,
        excepciones=excepciones,
        retardo_inicial=retardo_inicial,
        factor_backoff=factor_backoff,
        max_retardo=max_retardo,
        jitter=jitter,
    )
