import sys
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from core.performance import (
    optimizar,
    perfilar,
    smart_perfilar,
    optimizar_bucle,
)


def _dummy(x=0):
    return x + 1


def test_optimizar_decorator_invoca_auto_boost():
    def fake_auto_boost(*, workers=4, fallback=None):
        def decorator(func):
            def wrapper(*args, **kwargs):
                return func(*args, **kwargs)

            return wrapper

        return decorator

    with patch("core.performance.auto_boost", side_effect=fake_auto_boost) as ab:
        @optimizar(workers=2)
        def foo(x):
            return x + 1

        assert foo(1) == 2
        ab.assert_called_once_with(workers=2, fallback=None)


def test_optimizar_directo_invoca_auto_boost():
    def fake_auto_boost(*, workers=4, fallback=None):
        def decorator(func):
            def wrapper(*args, **kwargs):
                return func(*args, **kwargs)

            return wrapper

        return decorator

    with patch("core.performance.auto_boost", side_effect=fake_auto_boost) as ab:
        def bar(x):
            return x + 2

        wrapped = optimizar(bar, workers=3)
        assert wrapped(1) == 3
        ab.assert_called_once_with(workers=3, fallback=None)


def test_perfilar_invoca_profile_it():
    def suma(x, y):
        return x + y

    with patch("core.performance.profile_it", return_value={"mean": 1}) as pf:
        datos = perfilar(suma, args=(1, 2), repeticiones=3, paralelo=True)

    pf.assert_called_once_with(suma, args=(1, 2), kwargs={}, repeat=3, parallel=True)
    assert datos == {"mean": 1}


def test_smart_perfilar_invoca_smart_profile():
    with patch("core.performance.smart_profile", create=True, return_value={"mean": 1}) as sp:
        result = smart_perfilar(_dummy, args=(1,))
    sp.assert_called_once()
    assert result == {"mean": 1}


def test_optimizar_bucle_decorator():
    def fake_optimize_loop(loops=1, fallback=None):
        def decorator(func):
            def wrapper(*args, **kwargs):
                return func(*args, **kwargs)
            return wrapper
        return decorator

    with patch("core.performance.optimize_loop", create=True, side_effect=fake_optimize_loop) as op:
        @optimizar_bucle(loops=2)
        def foo():
            return "ok"

        assert foo() == "ok"
        op.assert_called_once_with(loops=2, fallback=None)
