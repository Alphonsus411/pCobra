import sys
from types import ModuleType

import pytest

fake_requests = ModuleType("requests")
fake_requests.Response = type("Response", (), {})
fake_requests.get = lambda *args, **kwargs: (_ for _ in ()).throw(RuntimeError("requests no disponible"))
fake_requests.post = lambda *args, **kwargs: (_ for _ in ()).throw(RuntimeError("requests no disponible"))
sys.modules.setdefault("requests", fake_requests)

import pcobra.corelibs as core


def test_mediana_lista_vacia():
    with pytest.raises(ValueError):
        core.mediana([])


def test_moda_lista_vacia():
    with pytest.raises(ValueError):
        core.moda([])


def test_desviacion_estandar_lista_vacia():
    with pytest.raises(ValueError):
        core.desviacion_estandar([])


def test_desviacion_estandar_muestral_requiere_dos_valores():
    with pytest.raises(ValueError):
        core.desviacion_estandar([1.0], muestral=True)


def test_raiz_validaciones():
    with pytest.raises(ValueError):
        core.raiz(4, 0)
    with pytest.raises(ValueError):
        core.raiz(-1, 2)
    with pytest.raises(ValueError):
        core.raiz(-8, 2.5)


def test_clamp_rango_invalido():
    with pytest.raises(ValueError):
        core.clamp(1, 5, 2)


def test_aleatorio_intervalo_invalido():
    with pytest.raises(ValueError):
        core.aleatorio(5, 1)


def test_mediana_negativos_y_precision():
    assert core.mediana([-5, -1, -3]) == -3
    assert core.mediana([0.1, 0.2, 0.3, 0.4]) == pytest.approx(0.25)


def test_redondear_precision():
    valor = core.redondear(2 / 3, 3)
    assert valor == pytest.approx(0.667, rel=1e-6)
