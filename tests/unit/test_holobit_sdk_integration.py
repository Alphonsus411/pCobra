import pytest
from core.holobits import Holobit, graficar, proyectar, transformar
from pcobra.cobra.cli.target_policies import SDK_COMPATIBLE_TARGETS
from pcobra.cobra.transpilers.compatibility_matrix import BACKEND_COMPATIBILITY, CONTRACT_FEATURES
from pcobra.cobra.transpilers.targets import OFFICIAL_TARGETS


def test_graficar_usa_sdk(monkeypatch):
    llamadas = {}
    def fake(hb):
        llamadas['hb'] = hb
    monkeypatch.setitem(graficar.__globals__, '_HOLOBIT_SDK_ERROR', None)
    monkeypatch.setitem(graficar.__globals__, 'proyectar_holograma', fake)
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
    monkeypatch.setitem(proyectar.__globals__, '_HOLOBIT_SDK_ERROR', None)
    monkeypatch.setitem(proyectar.__globals__, 'proyectar_holograma', fake)
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
    monkeypatch.setitem(transformar.__globals__, '_HOLOBIT_SDK_ERROR', None)
    monkeypatch.setattr('holobit_sdk.core.holobit.Holobit.rotar', fake_rotar)
    h = Holobit([1, 2, 3, 4, 5, 6])
    transformar(h, 'rotar', 'z', 45)
    assert args == {'eje': 'z', 'angulo': 45.0}


def test_python_es_el_unico_backend_con_sdk_full():
    assert SDK_COMPATIBLE_TARGETS == ("python",)
    for feature in CONTRACT_FEATURES:
        full_backends = {
            backend
            for backend in OFFICIAL_TARGETS
            if BACKEND_COMPATIBILITY[backend][feature] == "full"
        }
        assert full_backends == {"python"}


@pytest.mark.parametrize("backend", OFFICIAL_TARGETS)
def test_sdk_policy_y_matriz_coinciden_para_cada_target_oficial(backend: str):
    matrix_is_full = all(
        BACKEND_COMPATIBILITY[backend][feature] == "full"
        for feature in CONTRACT_FEATURES
    )
    policy_declares_sdk = backend in SDK_COMPATIBLE_TARGETS
    assert policy_declares_sdk is matrix_is_full
    if backend == "python":
        assert policy_declares_sdk
    else:
        assert not policy_declares_sdk
