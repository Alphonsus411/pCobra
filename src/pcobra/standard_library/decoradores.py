"""Decoradores utilitarios expuestos por :mod:`standard_library`.

Este módulo proporciona atajos en español para decorar funciones y clases
utilizando patrones comunes en Python, con un enfoque en mantener la
legibilidad al trabajar junto a Cobra.
"""

from __future__ import annotations

import inspect
import random
import threading
import time
import warnings
from dataclasses import dataclass as _dataclass
from functools import lru_cache as _lru_cache, wraps
import importlib.util
from typing import Any, Awaitable, Callable, Optional, ParamSpec, Sequence, TypeVar, overload

from pcobra.corelibs import reintentar_async as _reintentar_async

_rich_spec = importlib.util.find_spec("rich.console")
if _rich_spec is not None:
    from rich.console import Console  # type: ignore[assignment]
else:  # pragma: no cover - ``rich`` es opcional.
    Console = None  # type: ignore[assignment]


P = ParamSpec("P")
R = TypeVar("R")
T = TypeVar("T")


def _validar_parametros_reintento(
    *,
    intentos: int,
    retardo_inicial: float,
    factor_backoff: float,
    max_retardo: float | None,
) -> None:
    if intentos < 1:
        raise ValueError("intentos debe ser un entero positivo")
    if retardo_inicial < 0:
        raise ValueError("retardo_inicial no puede ser negativo")
    if factor_backoff <= 0:
        raise ValueError("factor_backoff debe ser mayor que cero")
    if max_retardo is not None and max_retardo < 0:
        raise ValueError("max_retardo no puede ser negativo")


def _normalizar_excepciones(
    excepciones: type[BaseException] | Sequence[type[BaseException]],
) -> tuple[type[BaseException], ...]:
    if isinstance(excepciones, type):
        tipos = (excepciones,)
    else:
        tipos = tuple(excepciones)

    if not tipos:
        raise ValueError("excepciones no puede estar vacío")

    for tipo in tipos:
        if not isinstance(tipo, type) or not issubclass(tipo, BaseException):
            raise TypeError("Cada entrada de excepciones debe ser una excepción")

    return tipos


def _crear_calculadora_espera(
    *,
    retardo_inicial: float,
    factor_backoff: float,
    max_retardo: float | None,
    jitter: Callable[[float], float]
    | tuple[float, float]
    | float
    | bool
    | None,
) -> Callable[[int], float]:
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
            minimo, maximo = float(jitter[0]), float(jitter[1])
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

    def _calcular(intento: int) -> float:
        espera = retardo_inicial * (factor_backoff ** (intento - 1))
        if max_retardo is not None:
            espera = min(espera, max_retardo)
        if espera <= 0:
            return 0.0
        return _aplicar_jitter(espera)

    return _calcular


@overload
def memoizar(funcion: Callable[P, R], /, *, maxsize: Optional[int] = ..., typed: bool = ...) -> Callable[P, R]:
    ...


@overload
def memoizar(*, maxsize: Optional[int] = ..., typed: bool = ...) -> Callable[[Callable[P, R]], Callable[P, R]]:
    ...


def memoizar(
    funcion: Callable[P, R] | None = None,
    /,
    *,
    maxsize: Optional[int] = 128,
    typed: bool = False,
) -> Callable[P, R] | Callable[[Callable[P, R]], Callable[P, R]]:
    """Cachea resultados de una función basada en sus argumentos.

    Es un envoltorio directo sobre :func:`functools.lru_cache` con un nombre en
    español para facilitar su descubrimiento desde Cobra.
    """

    def decorador(objetivo: Callable[P, R]) -> Callable[P, R]:
        return _lru_cache(maxsize=maxsize, typed=typed)(objetivo)

    if funcion is not None:
        return decorador(funcion)
    return decorador


@overload
def depreciado(
    funcion: Callable[P, R],
    /,
    *,
    mensaje: str | None = ...,
    categoria: type[Warning] = ...,
    consola: Console | None = ...,
    estilizar: bool = ...,
) -> Callable[P, R]:
    ...


@overload
def depreciado(
    *,
    mensaje: str | None = ...,
    categoria: type[Warning] = ...,
    consola: Console | None = ...,
    estilizar: bool = ...,
) -> Callable[[Callable[P, R]], Callable[P, R]]:
    ...


def depreciado(
    funcion: Callable[P, R] | None = None,
    /,
    *,
    mensaje: str | None = None,
    categoria: type[Warning] = DeprecationWarning,
    consola: Console | None = None,
    estilizar: bool = True,
) -> Callable[P, R] | Callable[[Callable[P, R]], Callable[P, R]]:
    """Marca ``funcion`` como obsoleta emitiendo una advertencia al usarla."""

    def decorador(objetivo: Callable[P, R]) -> Callable[P, R]:
        nombre = getattr(objetivo, "__qualname__", repr(objetivo))
        texto = mensaje or f"{nombre} está en desuso y puede eliminarse en futuras versiones."
        console = consola
        if console is None and estilizar and Console is not None:
            console = Console()

        if inspect.iscoroutinefunction(objetivo):

            @wraps(objetivo)
            async def wrapper_async(*args: P.args, **kwargs: P.kwargs) -> R:
                warnings.warn(texto, category=categoria, stacklevel=2)
                if estilizar and console is not None:
                    console.print(texto, style="bold yellow")
                return await objetivo(*args, **kwargs)

            return wrapper_async

        @wraps(objetivo)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            warnings.warn(texto, category=categoria, stacklevel=2)
            if estilizar and console is not None:
                console.print(texto, style="bold yellow")
            return objetivo(*args, **kwargs)

        return wrapper

    if funcion is not None:
        return decorador(funcion)
    return decorador


@overload
def sincronizar(
    funcion: Callable[P, R],
    /,
    *,
    candado: threading.Lock | threading.RLock | None = ...,
) -> Callable[P, R]:
    ...


@overload
def sincronizar(
    *,
    candado: threading.Lock | threading.RLock | None = ...,
) -> Callable[[Callable[P, R]], Callable[P, R]]:
    ...


def sincronizar(
    funcion: Callable[P, R] | None = None,
    /,
    *,
    candado: threading.Lock | threading.RLock | None = None,
) -> Callable[P, R] | Callable[[Callable[P, R]], Callable[P, R]]:
    """Protege ``funcion`` con un ``threading.Lock`` para evitar concurrencia."""

    def decorador(objetivo: Callable[P, R]) -> Callable[P, R]:
        if inspect.iscoroutinefunction(objetivo):
            raise TypeError(
                "sincronizar solo admite funciones síncronas; para corrutinas usa asyncio.Lock"
            )

        bloqueo = candado or threading.Lock()

        @wraps(objetivo)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            with bloqueo:
                return objetivo(*args, **kwargs)

        return wrapper

    if funcion is not None:
        return decorador(funcion)
    return decorador


@overload
def reintentar(
    funcion: Callable[P, R],
    /,
    *,
    intentos: int = ...,
    excepciones: type[BaseException] | Sequence[type[BaseException]] = ...,
    retardo_inicial: float = ...,
    factor_backoff: float = ...,
    max_retardo: float | None = ...,
    jitter: Callable[[float], float] | tuple[float, float] | float | bool | None = ...,
    etiqueta: str | None = ...,
    consola: Console | None = ...,
    estilizar: bool = ...,
) -> Callable[P, R]:
    ...


@overload
def reintentar(
    *,
    intentos: int = ...,
    excepciones: type[BaseException] | Sequence[type[BaseException]] = ...,
    retardo_inicial: float = ...,
    factor_backoff: float = ...,
    max_retardo: float | None = ...,
    jitter: Callable[[float], float] | tuple[float, float] | float | bool | None = ...,
    etiqueta: str | None = ...,
    consola: Console | None = ...,
    estilizar: bool = ...,
) -> Callable[[Callable[P, R]], Callable[P, R]]:
    ...


def reintentar(
    funcion: Callable[P, R] | None = None,
    /,
    *,
    intentos: int = 3,
    excepciones: type[BaseException] | Sequence[type[BaseException]] = (Exception,),
    retardo_inicial: float = 0.1,
    factor_backoff: float = 2.0,
    max_retardo: float | None = None,
    jitter: Callable[[float], float] | tuple[float, float] | float | bool | None = None,
    etiqueta: str | None = None,
    consola: Console | None = None,
    estilizar: bool = True,
) -> Callable[P, R] | Callable[[Callable[P, R]], Callable[P, R]]:
    """Reintenta ``funcion`` al fallar con *backoff* exponencial configurable."""

    _validar_parametros_reintento(
        intentos=intentos,
        retardo_inicial=retardo_inicial,
        factor_backoff=factor_backoff,
        max_retardo=max_retardo,
    )
    tipos_controlados = _normalizar_excepciones(excepciones)
    calcular_espera = _crear_calculadora_espera(
        retardo_inicial=retardo_inicial,
        factor_backoff=factor_backoff,
        max_retardo=max_retardo,
        jitter=jitter,
    )

    def decorador(objetivo: Callable[P, R]) -> Callable[P, R]:
        if inspect.iscoroutinefunction(objetivo):
            raise TypeError(
                "reintentar solo admite funciones síncronas; usa reintentar_async para corrutinas"
            )

        nombre = etiqueta or getattr(objetivo, "__qualname__", repr(objetivo))
        console = consola
        if console is None and estilizar and Console is not None:
            console = Console()

        def _emitir(intento_siguiente: int) -> None:
            mensaje = f"[reintentar:{nombre}] reintento {intento_siguiente}/{intentos}"
            if estilizar:
                if console is not None:
                    console.print(mensaje, style="bold yellow")
                else:
                    print(mensaje)

        @wraps(objetivo)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            ultimo_error: BaseException | None = None
            for numero_intento in range(1, intentos + 1):
                try:
                    return objetivo(*args, **kwargs)
                except tipos_controlados as exc:
                    ultimo_error = exc
                if numero_intento == intentos:
                    assert ultimo_error is not None
                    raise ultimo_error
                espera = calcular_espera(numero_intento)
                _emitir(numero_intento + 1)
                if espera > 0:
                    time.sleep(espera)
            assert ultimo_error is not None  # pragma: no cover - sanidad
            raise ultimo_error

        return wrapper

    if funcion is not None:
        return decorador(funcion)
    return decorador


@overload
def reintentar_async(
    funcion: Callable[P, Awaitable[R]],
    /,
    *,
    intentos: int = ...,
    excepciones: type[BaseException] | Sequence[type[BaseException]] = ...,
    retardo_inicial: float = ...,
    factor_backoff: float = ...,
    max_retardo: float | None = ...,
    jitter: Callable[[float], float] | tuple[float, float] | float | bool | None = ...,
    etiqueta: str | None = ...,
    consola: Console | None = ...,
    estilizar: bool = ...,
) -> Callable[P, Awaitable[R]]:
    ...


@overload
def reintentar_async(
    *,
    intentos: int = ...,
    excepciones: type[BaseException] | Sequence[type[BaseException]] = ...,
    retardo_inicial: float = ...,
    factor_backoff: float = ...,
    max_retardo: float | None = ...,
    jitter: Callable[[float], float] | tuple[float, float] | float | bool | None = ...,
    etiqueta: str | None = ...,
    consola: Console | None = ...,
    estilizar: bool = ...,
) -> Callable[[Callable[P, Awaitable[R]]], Callable[P, Awaitable[R]]]:
    ...


def reintentar_async(
    funcion: Callable[P, Awaitable[R]] | None = None,
    /,
    *,
    intentos: int = 3,
    excepciones: type[BaseException] | Sequence[type[BaseException]] = (Exception,),
    retardo_inicial: float = 0.1,
    factor_backoff: float = 2.0,
    max_retardo: float | None = None,
    jitter: Callable[[float], float] | tuple[float, float] | float | bool | None = None,
    etiqueta: str | None = None,
    consola: Console | None = None,
    estilizar: bool = True,
) -> Callable[P, Awaitable[R]] | Callable[[Callable[P, Awaitable[R]]], Callable[P, Awaitable[R]]]:
    """Equivalente asíncrono de :func:`reintentar` basado en ``corelibs``."""

    _validar_parametros_reintento(
        intentos=intentos,
        retardo_inicial=retardo_inicial,
        factor_backoff=factor_backoff,
        max_retardo=max_retardo,
    )
    tipos_controlados = _normalizar_excepciones(excepciones)

    def decorador(objetivo: Callable[P, Awaitable[R]]) -> Callable[P, Awaitable[R]]:
        if not inspect.iscoroutinefunction(objetivo):
            raise TypeError(
                "reintentar_async requiere una corrutina; usa reintentar para funciones síncronas"
            )

        nombre = etiqueta or getattr(objetivo, "__qualname__", repr(objetivo))
        console = consola
        if console is None and estilizar and Console is not None:
            console = Console()

        @wraps(objetivo)
        async def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            contador = 0

            async def _invocar() -> R:
                nonlocal contador
                contador += 1
                if estilizar and contador > 1:
                    mensaje = f"[reintentar:{nombre}] reintento {contador}/{intentos}"
                    if console is not None:
                        console.print(mensaje, style="bold yellow")
                    else:
                        print(mensaje)
                return await objetivo(*args, **kwargs)

            return await _reintentar_async(
                _invocar,
                intentos=intentos,
                excepciones=tipos_controlados,
                retardo_inicial=retardo_inicial,
                factor_backoff=factor_backoff,
                max_retardo=max_retardo,
                jitter=jitter,
            )

        return wrapper

    if funcion is not None:
        return decorador(funcion)
    return decorador


@overload
def dataclase(_cls: type[T], /, **opciones: Any) -> type[T]:
    ...


@overload
def dataclase(**opciones: Any) -> Callable[[type[T]], type[T]]:
    ...


def dataclase(_cls: type[T] | None = None, /, **opciones: Any) -> type[T] | Callable[[type[T]], type[T]]:
    """Alias en español para :func:`dataclasses.dataclass`.

    Todos los argumentos originales están disponibles a través de ``opciones``.
    """

    def decorador(clase: type[T]) -> type[T]:
        return _dataclass(**opciones)(clase)

    if _cls is not None:
        return decorador(_cls)
    return decorador


@overload
def temporizar(funcion: Callable[P, R], /, *, etiqueta: str | None = ..., precision: int = ..., consola: Console | None = ...) -> Callable[P, R]:
    ...


@overload
def temporizar(*, etiqueta: str | None = ..., precision: int = ..., consola: Console | None = ...) -> Callable[[Callable[P, R]], Callable[P, R]]:
    ...


def temporizar(
    funcion: Callable[P, R] | None = None,
    /,
    *,
    etiqueta: str | None = None,
    precision: int = 4,
    consola: Console | None = None,
) -> Callable[P, R] | Callable[[Callable[P, R]], Callable[P, R]]:
    """Mide y reporta la duración de cada invocación de ``funcion``.

    Por defecto imprime el resultado usando :class:`rich.console.Console` si está
    disponible. Cuando ``rich`` no puede importarse, se utiliza ``print``.
    """

    console = consola
    if console is None and Console is not None:
        console = Console()

    def decorador(objetivo: Callable[P, R]) -> Callable[P, R]:
        nombre = etiqueta or getattr(objetivo, "__qualname__", repr(objetivo))

        if inspect.iscoroutinefunction(objetivo):

            @wraps(objetivo)
            async def wrapper_async(*args: P.args, **kwargs: P.kwargs) -> R:
                inicio = time.perf_counter()
                resultado = await objetivo(*args, **kwargs)
                duracion = time.perf_counter() - inicio
                mensaje = f"[{nombre}] {duracion:.{precision}f} s"
                if console is not None:
                    console.print(mensaje)
                else:
                    print(mensaje)
                return resultado

            return wrapper_async

        @wraps(objetivo)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            inicio = time.perf_counter()
            resultado = objetivo(*args, **kwargs)
            duracion = time.perf_counter() - inicio
            mensaje = f"[{nombre}] {duracion:.{precision}f} s"
            if console is not None:
                console.print(mensaje)
            else:
                print(mensaje)
            return resultado

        return wrapper

    if funcion is not None:
        return decorador(funcion)
    return decorador


__all__ = [
    "memoizar",
    "dataclase",
    "temporizar",
    "depreciado",
    "sincronizar",
    "reintentar",
    "reintentar_async",
]
