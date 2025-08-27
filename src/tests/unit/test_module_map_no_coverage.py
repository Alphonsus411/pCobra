import builtins
import importlib


def test_get_toml_map_without_coverage(monkeypatch, tmp_path):
    original_import = builtins.__import__

    def fake_import(name, globals=None, locals=None, fromlist=(), level=0):
        if name.startswith("coverage"):
            raise ModuleNotFoundError
        return original_import(name, globals, locals, fromlist, level)

    monkeypatch.setattr(builtins, "__import__", fake_import)

    import cobra.transpilers.module_map as module_map
    importlib.reload(module_map)

    toml_file = tmp_path / "cobra.toml"
    toml_file.write_text("")
    monkeypatch.setenv("COBRA_TOML", str(toml_file))

    module_map._toml_cache = None
    assert module_map.get_toml_map() == {}

