from __future__ import annotations

import pytest

import pcobra.corelibs.configuracion as configuracion


def test_import_directo_y_all_presente() -> None:
    assert isinstance(configuracion.__all__, list)
    assert "leer_configuracion" in configuracion.__all__


def test_leer_ini_y_configuracion_con_tmp_path(tmp_path) -> None:
    ruta_ini = tmp_path / "app.ini"
    ruta_ini.write_text("[app]\nnombre = cobra\n", encoding="utf-8")

    assert configuracion.leer_ini(ruta_ini) == {"app": {"nombre": "cobra"}}
    assert configuracion.leer_configuracion(ruta_ini) == {"app": {"nombre": "cobra"}}


def test_extension_no_soportada_lanza_value_error(tmp_path) -> None:
    ruta = tmp_path / "app.txt"
    ruta.write_text("x=1", encoding="utf-8")

    with pytest.raises(ValueError):
        configuracion.leer_configuracion(ruta)
