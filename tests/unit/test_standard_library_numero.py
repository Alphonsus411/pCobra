from importlib import util
from pathlib import Path
import math
import sys
from types import ModuleType

import pytest


sys.modules.setdefault("httpx", ModuleType("httpx"))


def _cargar_numero():
    ruta = (
        Path(__file__).resolve().parents[2]
        / "src"
        / "pcobra"
        / "standard_library"
        / "numero.py"
    )
    spec = util.spec_from_file_location("standard_library.numero", ruta)
    modulo = util.module_from_spec(spec)
    if "standard_library" not in sys.modules:
        paquete = ModuleType("standard_library")
        paquete.__path__ = [str(ruta.parent)]
        sys.modules["standard_library"] = paquete
    sys.modules["standard_library.numero"] = modulo
    assert spec.loader is not None
    spec.loader.exec_module(modulo)
    return modulo


numero = _cargar_numero()


def test_es_finito_infinito_nan():
    assert numero.es_finito(10)
    assert not numero.es_finito(float("inf"))
    assert not numero.es_finito(float("nan"))
    assert numero.es_infinito(float("-inf"))
    assert not numero.es_infinito(0.0)
    assert numero.es_nan(float("nan"))
    assert not numero.es_nan(1.0)


def test_copiar_signo():
    assert numero.copiar_signo(5.0, -2.0) == pytest.approx(-5.0)
    resultado = numero.copiar_signo(0.0, -0.0)
    assert math.copysign(1.0, resultado) == -1.0
    nan = numero.copiar_signo(float("nan"), -1.0)
    assert math.isnan(nan)


def test_signo_y_limitar():
    assert numero.signo(-5) == -1
    assert numero.signo(0) == 0
    assert numero.signo(3.5) == pytest.approx(1.0)
    assert math.copysign(1.0, numero.signo(-0.0)) == -1.0
    assert math.isnan(numero.signo(float("nan")))

    assert numero.limitar(5, 0, 10) == 5
    assert numero.limitar(-5, -3, 3) == -3
    assert numero.limitar(2.5, 0.0, 1.0) == pytest.approx(1.0)
    assert math.isnan(numero.limitar(1.0, float("nan"), 5.0))
    assert math.isnan(numero.limitar(float("nan"), 0.0, 1.0))
    with pytest.raises(ValueError):
        numero.limitar(0, 2, 1)


def test_interpolar_y_envolver_modular():
    assert numero.interpolar(0.0, 10.0, 0.5) == pytest.approx(5.0)
    assert numero.interpolar(-5.0, 5.0, 3.0) == pytest.approx(5.0)
    assert numero.envolver_modular(7, 5) == 2
    assert numero.envolver_modular(-2, 5) == 3
    assert numero.envolver_modular(7.5, -5.0) == pytest.approx(-2.5)
    with pytest.raises(ZeroDivisionError):
        numero.envolver_modular(1, 0)


def test_raiz_entera_y_combinatoria():
    assert numero.raiz_entera(16) == 4
    assert numero.raiz_entera(10**12 + 12345) == 1000000
    with pytest.raises(ValueError):
        numero.raiz_entera(-9)

    assert numero.combinaciones(52, 5) == 2598960
    assert numero.permutaciones(10, 3) == 720
    assert numero.permutaciones(20, 6) == math.perm(20, 6)
    with pytest.raises(ValueError):
        numero.combinaciones(10, -1)
    with pytest.raises(ValueError):
        numero.permutaciones(10, -2)


def test_suma_precisa_precision():
    datos = [1e16, 1.0, -1e16]
    assert numero.suma_precisa(datos) == pytest.approx(1.0)
    with pytest.raises(TypeError):
        numero.suma_precisa([1.0, "no-num"])


@pytest.mark.parametrize(
    "funcion, argumentos",
    [
        (numero.es_finito, ("1",)),
        (numero.es_infinito, (object(),)),
        (numero.es_nan, (b"0",)),
        (numero.copiar_signo, ("1", 1)),
        (numero.signo, (object(),)),
        (numero.limitar, (1, "0", 2)),
        (numero.interpolar, (0, 1, "factor")),
        (numero.envolver_modular, (1, "0")),
        (numero.raiz_entera, ("9",)),
        (numero.combinaciones, (5.5, 2)),
        (numero.permutaciones, ("10", None)),
        (numero.suma_precisa, ([1, 2, object()],)),
    ],
)
def test_validaciones(funcion, argumentos):
    with pytest.raises(TypeError):
        funcion(*argumentos)
