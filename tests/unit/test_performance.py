import sys
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

import core.performance as perf


def test_perfilar_invoca_profile_it():
    def suma(x, y):
        return x + y

    with patch("core.performance.profile_it", return_value={"mean": 1}) as pf:
        datos = perf.perfilar(suma, args=(1, 2), repeticiones=3, paralelo=False)

    pf.assert_called_once_with(suma, args=(1, 2), kwargs={}, repeat=3, parallel=False)
    assert datos == {"mean": 1}


def test_bad_and_dangerous_directo():
    def suma(x, y):
        return x + y

    with patch("core.performance.bad_and_dangerous", return_value={"mean": 2}) as bd:
        datos = perf.bad_and_dangerous(
            suma, args=(1, 2), kwargs={}, repeat=5, parallel=True
        )

    bd.assert_called_once_with(
        suma, args=(1, 2), kwargs={}, repeat=5, parallel=True
    )
    assert datos == {"mean": 2}


def test_jam_decorator_directo():
    def fake_jam(*, loops=1, fallback=None):
        def decorator(func):
            def wrapper(*args, **kwargs):
                return func(*args, **kwargs)

            return wrapper

        return decorator

    with patch("core.performance.jam", side_effect=fake_jam) as jm:
        @perf.jam(loops=4)
        def foo(x):
            return x + 1

        assert foo(1) == 2
        jm.assert_called_once()
        assert jm.call_args.kwargs["loops"] == 4

