from __future__ import annotations

import importlib
import pytest

import pcobra.corelibs.serializacion as serializacion


def test_import_directo_y_all_presente() -> None:
    modulo = importlib.import_module("pcobra.corelibs.serializacion")

    assert modulo is serializacion
    assert isinstance(serializacion.__all__, list)
    assert "codificar_json" in serializacion.__all__
    assert callable(getattr(serializacion, "codificar_json"))


def test_json_y_csv_exitosos_con_tmp_path(tmp_path) -> None:
    ruta_json = tmp_path / "datos.json"
    serializacion.escribir_json(ruta_json, {"b": 2, "a": 1}, indentar=None)
    assert serializacion.leer_json(ruta_json) == {"a": 1, "b": 2}

    ruta_csv = tmp_path / "datos.csv"
    serializacion.escribir_csv(ruta_csv, [{"nombre": "Ada", "valor": 1}])
    assert serializacion.leer_csv(ruta_csv) == [{"nombre": "Ada", "valor": "1"}]


def test_decodificar_json_invalido_lanza_error() -> None:
    with pytest.raises(ValueError):
        serializacion.decodificar_json("{no-es-json")
