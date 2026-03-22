import builtins
import logging

from cobra.transpilers import module_map


def test_get_toml_map_missing_file_returns_empty_and_logs_error(monkeypatch, caplog):
    module_map._toml_cache = None
    monkeypatch.setattr(module_map, "COBRA_TOML_PATH", "missing.toml")
    monkeypatch.setattr(module_map.os.path, "exists", lambda path: True)

    def fake_open(*args, **kwargs):
        raise FileNotFoundError("missing")

    monkeypatch.setattr(builtins, "open", fake_open)

    with caplog.at_level(logging.ERROR):
        result = module_map.get_toml_map()

    assert result == {}
    assert "Error al cargar cobra.toml" in caplog.text


def test_get_toml_map_invalid_file_returns_empty_and_logs_error(tmp_path, monkeypatch, caplog):
    module_map._toml_cache = None
    bad_toml = tmp_path / "cobra.toml"
    bad_toml.write_text("invalid = ]")
    monkeypatch.setattr(module_map, "COBRA_TOML_PATH", str(bad_toml))

    with caplog.at_level(logging.ERROR):
        result = module_map.get_toml_map()

    assert result == {}
    assert "Error al cargar cobra.toml" in caplog.text


def test_get_mapped_path_returns_original_when_no_mapping(monkeypatch):
    monkeypatch.setattr(module_map, "get_toml_map", lambda: {})
    assert module_map.get_mapped_path("m", "python") == "m"


def test_get_mapped_path_devuelve_original_para_backend_fuera_del_set_canonico(monkeypatch):
    monkeypatch.setattr(
        module_map,
        "get_toml_map",
        lambda: {"modulos": {"m": {"javascript": "dist/m.js"}}},
    )
    assert module_map.get_mapped_path("m", "fantasy") == "m"


def test_get_mapped_path_resuelve_desde_tabla_modulos_en_toml(monkeypatch):
    monkeypatch.setattr(
        module_map,
        "get_toml_map",
        lambda: {"modulos": {"m": {"javascript": "dist/m.js"}}},
    )
    assert module_map.get_mapped_path("m", "javascript") == "dist/m.js"


def test_get_mapped_path_ignora_mappings_en_raiz_legacy(monkeypatch):
    monkeypatch.setattr(module_map, "get_toml_map", lambda: {"m": {"javascript": "m.js"}})
    assert module_map.get_mapped_path("m", "javascript") == "m"
