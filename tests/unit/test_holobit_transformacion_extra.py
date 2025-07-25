import pytest
from core.holobits import Holobit, escalar, mover


def test_escalar_usa_sdk(monkeypatch):
    args = {}
    def fake_escalar(self, factor):
        args['factor'] = factor
    monkeypatch.setattr('holobit_sdk.core.holobit.Holobit.escalar', fake_escalar, raising=False)
    h = Holobit([1, 2, 3])
    escalar(h, 2)
    assert args == {'factor': 2.0}


def test_mover_usa_sdk(monkeypatch):
    args = {}
    def fake_mover(self, x, y, z):
        args['x'] = x
        args['y'] = y
        args['z'] = z
    monkeypatch.setattr('holobit_sdk.core.holobit.Holobit.mover', fake_mover, raising=False)
    h = Holobit([1, 2, 3])
    mover(h, 0.5, -1.0, 2.0)
    assert args == {'x': 0.5, 'y': -1.0, 'z': 2.0}
