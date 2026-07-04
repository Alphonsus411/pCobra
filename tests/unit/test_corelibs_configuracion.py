from __future__ import annotations

from pathlib import Path

import pytest

from pcobra.corelibs import configuracion


def test_leer_toml_y_leer_configuracion_toml(tmp_path: Path):
    ruta = tmp_path / "app.toml"
    ruta.write_text('[app]\nnombre = "Cobra"\nactivo = true\n', encoding="utf-8")

    assert configuracion.toml_disponible() is True
    assert configuracion.leer_toml(ruta) == {"app": {"nombre": "Cobra", "activo": True}}
    assert configuracion.leer_configuracion(ruta) == {"app": {"nombre": "Cobra", "activo": True}}


def test_leer_ini_y_cfg_por_extension(tmp_path: Path):
    ruta = tmp_path / "app.cfg"
    ruta.write_text('[DEFAULT]\nbase = cobra\n[servidor]\npuerto = 8080\n', encoding="utf-8")

    assert configuracion.leer_ini(ruta) == {
        "DEFAULT": {"base": "cobra"},
        "servidor": {"base": "cobra", "puerto": "8080"},
    }
    assert configuracion.leer_configuracion(ruta)["servidor"]["puerto"] == "8080"


def test_leer_toml_sin_tomllib_lanza_runtimeerror_claro(tmp_path: Path, monkeypatch):
    ruta = tmp_path / "app.toml"
    ruta.write_text("valor = 1\n", encoding="utf-8")
    monkeypatch.setattr(configuracion, "toml_disponible", lambda: False)

    with pytest.raises(RuntimeError, match="TOML no está soportado.*tomllib"):
        configuracion.leer_toml(ruta)


def test_errores_deterministas_para_ruta_inexistente_y_formato_no_soportado(tmp_path: Path):
    inexistente = tmp_path / "no_existe.ini"
    with pytest.raises(FileNotFoundError, match="Archivo de configuración no encontrado"):
        configuracion.leer_configuracion(inexistente)

    ruta = tmp_path / "app.json"
    ruta.write_text("{}", encoding="utf-8")
    with pytest.raises(ValueError, match="Formato de configuración no soportado"):
        configuracion.leer_configuracion(ruta)


def test_all_expone_solo_api_publica():
    assert configuracion.__all__ == [
        "leer_toml",
        "leer_ini",
        "toml_disponible",
        "leer_configuracion",
    ]
