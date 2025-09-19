from importlib import util
from pathlib import Path
import math
import sys
from types import ModuleType

import pytest


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


@pytest.mark.parametrize(
    "funcion, argumentos",
    [
        (numero.es_finito, ("1",)),
        (numero.es_infinito, (object(),)),
        (numero.es_nan, (b"0",)),
        (numero.copiar_signo, ("1", 1)),
    ],
)
def test_validaciones(funcion, argumentos):
    with pytest.raises(TypeError):
        funcion(*argumentos)
