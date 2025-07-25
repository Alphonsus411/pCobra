import pytest
import numpy as np
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


def test_escalar_fallback(monkeypatch):
    class DummyQuark:
        def __init__(self, pos):
            self.posicion = np.array(pos, dtype=float)

    class DummyHolobit:
        def __init__(self):
            self.quarks = [DummyQuark([1, 0, 0])]
            self.antiquarks = [DummyQuark([-1, 0, 0])]

    dummy = DummyHolobit()
    monkeypatch.setattr('core.holobits.transformacion._to_sdk_holobit', lambda hb: dummy)
    escalar(Holobit([1, 2, 3]), 3)
    assert np.allclose(dummy.quarks[0].posicion, [3, 0, 0])
    assert np.allclose(dummy.antiquarks[0].posicion, [-3, 0, 0])


def test_mover_fallback(monkeypatch):
    class DummyQuark:
        def __init__(self, pos):
            self.posicion = np.array(pos, dtype=float)

    class DummyHolobit:
        def __init__(self):
            self.quarks = [DummyQuark([0, 1, 0])]
            self.antiquarks = []

    dummy = DummyHolobit()
    monkeypatch.setattr('core.holobits.transformacion._to_sdk_holobit', lambda hb: dummy)
    mover(Holobit([1, 2, 3]), -1, 2, 1)
    assert np.allclose(dummy.quarks[0].posicion, [-1, 3, 1])

