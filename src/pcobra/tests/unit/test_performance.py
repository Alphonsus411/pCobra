import sys
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from core.performance import smart_perfilar, optimizar_bucle


def _dummy(x=0):
    return x + 1


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
