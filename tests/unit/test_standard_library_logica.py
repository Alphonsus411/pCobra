from importlib import util
from pathlib import Path
import sys
from types import ModuleType

import pytest


def _cargar_logica():
    ruta = Path(__file__).resolve().parents[2] / "src" / "pcobra" / "standard_library" / "logica.py"
    spec = util.spec_from_file_location("standard_library.logica", ruta)
    modulo = util.module_from_spec(spec)
    if "standard_library" not in sys.modules:
        paquete = ModuleType("standard_library")
        paquete.__path__ = [str(ruta.parent)]
        sys.modules["standard_library"] = paquete
    sys.modules["standard_library.logica"] = modulo
    assert spec.loader is not None
    spec.loader.exec_module(modulo)
    return modulo


logica = _cargar_logica()


def test_es_verdadero_y_es_falso():
    assert logica.es_verdadero(True) is True
    assert logica.es_verdadero(False) is False
    assert logica.es_falso(True) is False
    assert logica.es_falso(False) is True


def test_es_verdadero_es_falso_tipos_invalidos():
    for valor in (1, "False", None):
        with pytest.raises(TypeError):
            logica.es_verdadero(valor)
        with pytest.raises(TypeError):
            logica.es_falso(valor)
