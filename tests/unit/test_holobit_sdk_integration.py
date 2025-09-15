import pytest
from core.holobits import Holobit, graficar, proyectar, transformar


def test_graficar_usa_sdk(monkeypatch):
    llamadas = {}
    def fake(hb):
        llamadas['hb'] = hb
    import importlib
    gmod = importlib.import_module('core.holobits.graficar')
    monkeypatch.setattr(gmod, 'proyectar_holograma', fake)
    h = Holobit([1, 2, 3, 4, 5, 6])
    graficar(h)
    assert 'hb' in llamadas


def test_graficar_rechaza_valor_incorrecto():
    with pytest.raises(TypeError):
        graficar(None)


def test_proyectar_usa_sdk(monkeypatch):
    llamadas = {}
    def fake(hb):
        llamadas['hb'] = hb
    import importlib
    pmod = importlib.import_module('core.holobits.proyeccion')
    monkeypatch.setattr(pmod, 'proyectar_holograma', fake)
    h = Holobit([1, 2, 3, 4, 5, 6])
    proyectar(h, '2D')
    assert 'hb' in llamadas


def test_proyectar_rechaza_valor_incorrecto():
    with pytest.raises(TypeError):
        proyectar(None, '2D')


def test_transformar_usa_sdk(monkeypatch):
    args = {}
    def fake_rotar(self, eje, angulo):
        args['eje'] = eje
        args['angulo'] = angulo
    monkeypatch.setattr('holobit_sdk.core.holobit.Holobit.rotar', fake_rotar)
    h = Holobit([1, 2, 3, 4, 5, 6])
    transformar(h, 'rotar', 'z', 45)
    assert args == {'eje': 'z', 'angulo': 45.0}
