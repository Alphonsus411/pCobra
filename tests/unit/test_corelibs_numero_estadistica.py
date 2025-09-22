import math
import sys
from types import ModuleType

import pytest

fake_requests = ModuleType("requests")
fake_requests.Response = type("Response", (), {})
fake_requests.get = lambda *args, **kwargs: (_ for _ in ()).throw(RuntimeError("requests no disponible"))
fake_requests.post = lambda *args, **kwargs: (_ for _ in ()).throw(RuntimeError("requests no disponible"))
sys.modules.setdefault("requests", fake_requests)
sys.modules.setdefault("httpx", ModuleType("httpx"))

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


def test_varianza_validaciones():
    with pytest.raises(ValueError):
        core.varianza([])
    with pytest.raises(ValueError):
        core.varianza_muestral([1.0])
    with pytest.raises(TypeError):
        core.varianza([1.0, "texto"])  # type: ignore[arg-type]


def test_medias_avanzadas_validaciones():
    with pytest.raises(ValueError):
        core.media_geometrica([])
    with pytest.raises(ValueError):
        core.media_armonica([])
    with pytest.raises(ValueError):
        core.media_geometrica([-1, 2, 3])
    with pytest.raises(ValueError):
        core.media_armonica([-1, 1, 3])


def test_percentil_validaciones():
    with pytest.raises(ValueError):
        core.percentil([], 50)
    with pytest.raises(ValueError):
        core.percentil([1, 2, 3], -10)
    with pytest.raises(ValueError):
        core.percentil([1, 2, 3], 150)
    with pytest.raises(TypeError):
        core.percentil(object(), 50)  # type: ignore[arg-type]
    resultado_nan = core.percentil([1, 2, 3], float("nan"))
    assert math.isnan(resultado_nan)


def test_cuartiles_y_coeficiente_variacion_validaciones():
    with pytest.raises(ValueError):
        core.cuartiles([])
    with pytest.raises(ValueError):
        core.rango_intercuartil([])
    with pytest.raises(ValueError):
        core.coeficiente_variacion([1, -1])
    with pytest.raises(ValueError):
        core.coeficiente_variacion([5.0], muestral=True)


def test_raiz_validaciones():
    with pytest.raises(ValueError):
        core.raiz(4, 0)
    with pytest.raises(ValueError):
        core.raiz(-1, 2)
    with pytest.raises(ValueError):
        core.raiz(-8, 2.5)


def test_raiz_entera_y_combinatoria_core():
    assert core.raiz_entera(81) == 9
    assert core.raiz_entera(True) == 1
    with pytest.raises(ValueError):
        core.raiz_entera(-16)
    with pytest.raises(ValueError):
        core.raiz_entera(7.5)

    assert core.combinaciones(100, 4) == math.comb(100, 4)
    assert core.permutaciones(12, 6) == math.perm(12, 6)
    with pytest.raises(ValueError):
        core.combinaciones(12, -3)
    with pytest.raises(ValueError):
        core.permutaciones(8, -1)
    with pytest.raises(TypeError):
        core.combinaciones(5.5, 2)


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


def test_entero_a_base_validaciones():
    with pytest.raises(ValueError):
        core.entero_a_base(10, 1)
    with pytest.raises(ValueError):
        core.entero_a_base(10, 37)
    with pytest.raises(TypeError):
        core.entero_a_base(3.14, 10)


def test_entero_desde_base_validaciones():
    with pytest.raises(ValueError):
        core.entero_desde_base("", 10)
    with pytest.raises(ValueError):
        core.entero_desde_base("102", 2)
    with pytest.raises(ValueError):
        core.entero_desde_base("A", 16, alfabeto="0123456789ABCDEF"[:-1])


def test_producto_lista_vacia():
    assert core.producto([]) == 1


def test_suma_precisa_core():
    datos = [1e16, 1.0, -1e16]
    assert core.suma_precisa(datos) == pytest.approx(1.0)
    with pytest.raises(TypeError):
        core.suma_precisa([1, object()])
