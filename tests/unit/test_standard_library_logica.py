from importlib import util
from pathlib import Path
import sys
from types import ModuleType
from unittest.mock import MagicMock

import pytest

sys.modules.setdefault("httpx", ModuleType("httpx"))


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


def test_entonces_si_no_valores_directos():
    assert logica.entonces(True, "dato") == "dato"
    assert logica.entonces(False, "dato") is None
    assert logica.si_no(False, 7) == 7
    assert logica.si_no(True, 7) is None


def test_entonces_si_no_perezoso():
    accion = MagicMock(return_value="llamado")
    assert logica.entonces(True, accion) == "llamado"
    accion.assert_called_once_with()

    accion.reset_mock()
    accion.return_value = "omitido"
    assert logica.entonces(False, accion) is None
    accion.assert_not_called()

    accion.reset_mock()
    accion.return_value = "otro"
    assert logica.si_no(False, accion) == "otro"
    accion.assert_called_once_with()

    accion.reset_mock()
    accion.return_value = None
    assert logica.si_no(True, accion) is None
    accion.assert_not_called()


def test_condicional_evalua_en_orden():
    condicion1 = MagicMock(return_value=False)
    condicion2 = MagicMock(return_value=True)
    condicion3 = MagicMock(return_value=True)
    resultado1 = MagicMock(return_value="uno")
    resultado2 = MagicMock(return_value="dos")
    resultado3 = MagicMock(return_value="tres")

    valor = logica.condicional(
        (condicion1, resultado1),
        (condicion2, resultado2),
        (condicion3, resultado3),
    )

    assert valor == "dos"
    condicion1.assert_called_once_with()
    condicion2.assert_called_once_with()
    condicion3.assert_not_called()
    resultado1.assert_not_called()
    resultado2.assert_called_once_with()
    resultado3.assert_not_called()


def test_condicional_por_defecto_perezoso():
    condicion = MagicMock(return_value=False)
    resultado = MagicMock(return_value="omitido")
    por_defecto = MagicMock(return_value="valor")

    obtenido = logica.condicional((condicion, resultado), por_defecto=por_defecto)

    assert obtenido == "valor"
    condicion.assert_called_once_with()
    resultado.assert_not_called()
    por_defecto.assert_called_once_with()
