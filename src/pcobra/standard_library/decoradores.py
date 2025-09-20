"""Decoradores utilitarios expuestos por :mod:`standard_library`.

Este módulo proporciona atajos en español para decorar funciones y clases
utilizando patrones comunes en Python, con un enfoque en mantener la
legibilidad al trabajar junto a Cobra.
"""

from __future__ import annotations

import inspect
import time
from dataclasses import dataclass as _dataclass
from functools import lru_cache as _lru_cache, wraps
import importlib.util
from typing import Any, Callable, Optional, ParamSpec, TypeVar, overload

_rich_spec = importlib.util.find_spec("rich.console")
if _rich_spec is not None:
    from rich.console import Console  # type: ignore[assignment]
else:  # pragma: no cover - ``rich`` es opcional.
    Console = None  # type: ignore[assignment]


P = ParamSpec("P")
R = TypeVar("R")
T = TypeVar("T")


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


__all__ = ["memoizar", "dataclase", "temporizar"]
