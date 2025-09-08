"""Funciones de rendimiento basadas en smooth-criminal."""

from typing import Callable, Any
try:
    from smooth_criminal.core import (
        bad,
        profile_it,
        bad_and_dangerous,
        jam,
    )
except Exception:  # pragma: no cover - fallback when library is missing
    def bad(*, workers=4, fallback=None):
        def decorator(func):
            return func

        return decorator

    def profile_it(func, *, args=None, kwargs=None, repeat=1, parallel=False):
        return {}

    def bad_and_dangerous(
        func, *, args=None, kwargs=None, repeat=1, parallel=False
    ):
        return profile_it(
            func, args=args, kwargs=kwargs, repeat=repeat, parallel=parallel
        )

    def jam(*, loops=1, fallback=None):
        def decorator(func):
            return func

        return decorator


def optimizar(
    func: Callable | None = None, *, workers: int = 4, fallback: Callable | None = None
) -> Callable:
    """Devuelve una versión optimizada de ``func`` usando ``bad``.

    Puede usarse como decorador o llamando ``optimizar(func)`` directamente.
    """
    if func is None:

        def decorator(f: Callable) -> Callable:
            return bad(workers=workers, fallback=fallback)(f)

        return decorator
    return bad(workers=workers, fallback=fallback)(func)


def perfilar(
    func: Callable,
    *,
    args: tuple | None = None,
    kwargs: dict | None = None,
    repeticiones: int = 5,
    paralelo: bool = False
) -> dict[str, Any]:
    """Ejecuta ``func`` varias veces y devuelve estadísticas de rendimiento."""
    args = args or ()
    kwargs = kwargs or {}
    return profile_it(
        func, args=args, kwargs=kwargs, repeat=repeticiones, parallel=paralelo
    )


def smart_perfilar(
    func: Callable,
    *,
    args: tuple | None = None,
    kwargs: dict | None = None,
    repeticiones: int = 5,
    paralelo: bool = False
) -> dict[str, Any]:
    """Perfila ``func`` usando ``bad_and_dangerous`` o ``profile_it``."""
    args = args or ()
    kwargs = kwargs or {}
    try:
        return bad_and_dangerous(
            func, args=args, kwargs=kwargs, repeat=repeticiones, parallel=paralelo
        )
    except Exception:
        return profile_it(
            func, args=args, kwargs=kwargs, repeat=repeticiones, parallel=paralelo
        )


def optimizar_bucle(
    func: Callable | None = None,
    *,
    loops: int = 1,
    fallback: Callable | None = None,
) -> Callable:
    """Optimiza bucles dentro de ``func`` usando ``jam``."""
    if func is None:

        def decorator(f: Callable) -> Callable:
            return jam(loops=loops, fallback=fallback)(f)

        return decorator
    return jam(loops=loops, fallback=fallback)(func)
