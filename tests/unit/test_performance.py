import sys
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from core.performance import (
    smart_perfilar,
    optimizar_bucle,
)


def test_optimizar_bucle_decorator_invoca_jam():
    def fake_jam(*, loops=1, fallback=None):
        def decorator(func):
            def wrapper(*args, **kwargs):
                return func(*args, **kwargs)

            return wrapper

        return decorator

    with patch("core.performance.jam", side_effect=fake_jam) as jm:
        @optimizar_bucle(loops=5)
        def foo(x):
            return x + 1

        assert foo(1) == 2
        jm.assert_called_once_with(loops=5, fallback=None)


def test_optimizar_bucle_directo_invoca_jam():
    def fake_jam(*, loops=1, fallback=None):
        def decorator(func):
            def wrapper(*args, **kwargs):
                return func(*args, **kwargs)

            return wrapper

        return decorator

    with patch("core.performance.jam", side_effect=fake_jam) as jm:
        def bar(x):
            return x + 2

        wrapped = optimizar_bucle(bar, loops=3)
        assert wrapped(1) == 3
        jm.assert_called_once_with(loops=3, fallback=None)


def test_smart_perfilar_invoca_bad_and_dangerous():
    def suma(x, y):
        return x + y

    with patch("core.performance.bad_and_dangerous", return_value={"mean": 1}) as bd:
        datos = smart_perfilar(suma, args=(1, 2), repeticiones=3, paralelo=True)

    bd.assert_called_once_with(suma, args=(1, 2), kwargs={}, repeat=3, parallel=True)
    assert datos == {"mean": 1}


def test_smart_perfilar_fallback_a_profile_it():
    def suma(x, y):
        return x + y

    with patch("core.performance.bad_and_dangerous", side_effect=Exception("fail")) as bd, patch(
        "core.performance.profile_it", return_value={"mean": 2}
    ) as pf:
        datos = smart_perfilar(suma, args=(1, 2), repeticiones=4, paralelo=False)

    bd.assert_called_once_with(suma, args=(1, 2), kwargs={}, repeat=4, parallel=False)
    pf.assert_called_once_with(suma, args=(1, 2), kwargs={}, repeat=4, parallel=False)
    assert datos == {"mean": 2}
