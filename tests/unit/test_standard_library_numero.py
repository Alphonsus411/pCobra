from importlib import util
from pathlib import Path
import math
import statistics as stats
import sys
from types import ModuleType

import numpy as np
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


def test_hipotenusa_y_distancia_euclidiana():
    assert numero.hipotenusa(3, 4) == pytest.approx(5.0)
    assert numero.hipotenusa([2, 3, 6]) == pytest.approx(math.sqrt(49.0))

    punto_a = (0.0, 0.0, 0.0)
    punto_b = (1.0, 2.0, 2.0)
    assert numero.distancia_euclidiana(punto_a, punto_b) == pytest.approx(3.0)

    with pytest.raises(TypeError):
        numero.hipotenusa()
    with pytest.raises(TypeError):
        numero.hipotenusa("34")
    with pytest.raises(TypeError):
        numero.distancia_euclidiana("00", "11")
    with pytest.raises(TypeError):
        numero.distancia_euclidiana([1, "b"], [0, 0])
    with pytest.raises(ValueError):
        numero.distancia_euclidiana([0.0, 0.0], [1.0])


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


def test_estadisticas_avanzadas():
    datos = [2, 4, 4, 4, 5, 5, 7, 9]
    assert numero.varianza(datos) == pytest.approx(stats.pvariance(datos))
    assert numero.varianza_muestral(datos) == pytest.approx(stats.variance(datos))

    geometrica = [1, 3, 9, 27]
    assert numero.media_geometrica(geometrica) == pytest.approx(
        stats.geometric_mean(geometrica)
    )
    armonica = [1.5, 2.5, 4.0]
    assert numero.media_armonica(armonica) == pytest.approx(
        stats.harmonic_mean(armonica)
    )
    assert numero.media_armonica([1.0, 0.0, 3.0]) == pytest.approx(
        stats.harmonic_mean([1.0, 0.0, 3.0])
    )

    assert numero.percentil(datos, 25) == pytest.approx(
        float(np.percentile(datos, 25, method="linear"))
    )
    q1, q2, q3 = numero.cuartiles(datos)
    assert q1 == pytest.approx(float(np.percentile(datos, 25, method="linear")))
    assert q2 == pytest.approx(float(np.percentile(datos, 50, method="linear")))
    assert q3 == pytest.approx(float(np.percentile(datos, 75, method="linear")))
    assert numero.rango_intercuartil(datos) == pytest.approx(q3 - q1)

    coef_poblacional = stats.pstdev(datos) / abs(stats.fmean(datos))
    coef_muestral = stats.stdev(datos) / abs(stats.fmean(datos))
    assert numero.coeficiente_variacion(datos) == pytest.approx(coef_poblacional)
    assert numero.coeficiente_variacion(datos, muestral=True) == pytest.approx(
        coef_muestral
    )


def test_estadisticas_avanzadas_validaciones():
    with pytest.raises(ValueError):
        numero.varianza([])
    with pytest.raises(ValueError):
        numero.varianza_muestral([1.0])
    with pytest.raises(ValueError):
        numero.media_geometrica([-1, 1, 2])
    with pytest.raises(ValueError):
        numero.media_armonica([-1, 1, 3])
    with pytest.raises(ValueError):
        numero.percentil([], 50)
    with pytest.raises(ValueError):
        numero.percentil([1, 2, 3], 120)
    assert math.isnan(numero.percentil([1, 2, 3], float("nan")))
    with pytest.raises(ValueError):
        numero.cuartiles([])
    with pytest.raises(ValueError):
        numero.rango_intercuartil([])
    with pytest.raises(ValueError):
        numero.coeficiente_variacion([1, -1])
    with pytest.raises(ValueError):
        numero.coeficiente_variacion([10.0], muestral=True)


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
        (numero.hipotenusa, ()),
        (numero.hipotenusa, ("34",)),
        (numero.distancia_euclidiana, ("00", "11")),
        (numero.distancia_euclidiana, ([1, "b"], [0, 0])),
        (numero.raiz_entera, ("9",)),
        (numero.combinaciones, (5.5, 2)),
        (numero.permutaciones, ("10", None)),
        (numero.suma_precisa, ([1, 2, object()],)),
        (numero.varianza, ([1, object()],)),
        (numero.media_geometrica, ([1, object()],)),
        (numero.media_armonica, ([1, object()],)),
        (numero.percentil, ([1, 2, 3], "50")),
        (numero.coeficiente_variacion, ([1, object()],)),
    ],
)
def test_validaciones(funcion, argumentos):
    with pytest.raises(TypeError):
        funcion(*argumentos)
