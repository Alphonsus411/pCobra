import builtins
import logging


from cobra.transpilers import module_map


def test_get_map_missing_file_returns_empty_and_logs_error(monkeypatch, caplog):
    module_map._cache = None
    monkeypatch.setattr(module_map, "MODULE_MAP_PATH", "missing.mod")
    monkeypatch.setattr(module_map.os.path, "exists", lambda path: True)

    def fake_open(*args, **kwargs):
        raise FileNotFoundError("missing")

    monkeypatch.setattr(builtins, "open", fake_open)

    with caplog.at_level(logging.ERROR):
        result = module_map.get_map()

    assert result == {}
    assert "Error al cargar el archivo de mapeo" in caplog.text


def test_get_map_corrupt_yaml_returns_empty_and_logs_error(tmp_path, monkeypatch, caplog):
    module_map._cache = None
    bad_file = tmp_path / "cobra.mod"
    bad_file.write_text("foo: [1, 2")
    monkeypatch.setattr(module_map, "MODULE_MAP_PATH", str(bad_file))

    with caplog.at_level(logging.ERROR):
        result = module_map.get_map()

    assert result == {}
    assert "Error al cargar el archivo de mapeo" in caplog.text


def test_get_toml_map_missing_file_returns_empty_and_logs_error(monkeypatch, caplog):
    module_map._toml_cache = None
    monkeypatch.setattr(module_map, "PCOBRA_TOML_PATH", "missing.toml")
    monkeypatch.setattr(module_map.os.path, "exists", lambda path: True)

    def fake_open(*args, **kwargs):
        raise FileNotFoundError("missing")

    monkeypatch.setattr(builtins, "open", fake_open)

    with caplog.at_level(logging.ERROR):
        result = module_map.get_toml_map()

    assert result == {}
    assert "Error al cargar pcobra.toml" in caplog.text


def test_get_toml_map_invalid_file_returns_empty_and_logs_error(tmp_path, monkeypatch, caplog):
    module_map._toml_cache = None
    bad_toml = tmp_path / "pcobra.toml"
    bad_toml.write_text("invalid = ]")
    monkeypatch.setattr(module_map, "PCOBRA_TOML_PATH", str(bad_toml))

    with caplog.at_level(logging.ERROR):
        result = module_map.get_toml_map()

    assert result == {}
    assert "Error al cargar pcobra.toml" in caplog.text


def test_get_mapped_path_returns_original_when_no_mapping(monkeypatch):
    monkeypatch.setattr(module_map, "get_toml_map", lambda: {})
    assert module_map.get_mapped_path("m", "python") == "m"
