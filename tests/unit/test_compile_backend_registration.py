import importlib
import importlib.metadata
import types

import pytest

from pcobra.cobra.transpilers import registry as transpiler_registry


class DummyTranspiler:
    def generate_code(self, ast):
        return str(ast)


@pytest.fixture(autouse=True)
def clean_plugin_registry(monkeypatch):
    monkeypatch.setattr(transpiler_registry, "_PLUGIN_TRANSPILERS", {})
    monkeypatch.setattr(transpiler_registry, "_ENTRYPOINTS_LOADED", False)


def test_register_transpiler_backend_rechaza_backend_no_oficial():
    with pytest.raises(
        ValueError, match=r"Backend no permitido en tests: backend_no_soportado"
    ):
        transpiler_registry.register_transpiler_backend(
            "backend_no_soportado", DummyTranspiler, context="tests"
        )


def test_register_transpiler_backend_rechaza_alias_no_canonico():
    with pytest.raises(ValueError, match=r"sin alias"):
        transpiler_registry.register_transpiler_backend(" Python ", DummyTranspiler, context="tests")


def test_register_transpiler_backend_acepta_backend_canonico():
    canonical = transpiler_registry.register_transpiler_backend(
        "javascript", DummyTranspiler, context="tests"
    )

    assert canonical == "javascript"
    assert transpiler_registry.plugin_transpilers()["javascript"] is DummyTranspiler


def test_register_transpiler_backend_rechaza_duplicados():
    transpiler_registry.register_transpiler_backend("python", DummyTranspiler, context="tests")
    with pytest.raises(ValueError, match=r"Registro duplicado"):
        transpiler_registry.register_transpiler_backend("python", DummyTranspiler, context="tests")


def test_load_entrypoint_transpilers_omite_backend_fuera_del_set_oficial(monkeypatch, caplog):
    ep = importlib.metadata.EntryPoint(
        name="fantasy",
        value="tests.unit.test_compile_backend_registration:DummyTranspiler",
        group="cobra.transpilers",
    )
    monkeypatch.setattr(
        transpiler_registry,
        "_iter_transpiler_entry_points",
        lambda: importlib.metadata.EntryPoints((ep,)),
    )

    transpiler_registry.load_entrypoint_transpilers()

    assert dict(transpiler_registry.plugin_transpilers()) == {}
    assert "rechazado por política/contrato" in caplog.text


def test_load_entrypoint_transpilers_rechaza_alias_no_canonico(monkeypatch, caplog):
    ep = importlib.metadata.EntryPoint(
        name="Python",
        value="tests.unit.test_compile_backend_registration:DummyTranspiler",
        group="cobra.transpilers",
    )
    monkeypatch.setattr(
        transpiler_registry,
        "_iter_transpiler_entry_points",
        lambda: importlib.metadata.EntryPoints((ep,)),
    )

    transpiler_registry.load_entrypoint_transpilers()

    assert dict(transpiler_registry.plugin_transpilers()) == {}
    assert "entry points solo pueden usar nombres canónicos" in caplog.text


def test_load_entrypoint_transpilers_registra_backend_canonico(monkeypatch):
    ep = importlib.metadata.EntryPoint(
        name="python",
        value="fake.module:DummyExternalTranspiler",
        group="cobra.transpilers",
    )
    monkeypatch.setattr(
        transpiler_registry,
        "_iter_transpiler_entry_points",
        lambda: importlib.metadata.EntryPoints((ep,)),
    )
    monkeypatch.setattr(
        transpiler_registry,
        "import_module",
        lambda _name: types.SimpleNamespace(DummyExternalTranspiler=DummyTranspiler),
    )

    transpiler_registry.load_entrypoint_transpilers()

    assert dict(transpiler_registry.plugin_transpilers()) == {"python": DummyTranspiler}


def test_load_entrypoint_transpilers_no_sobrescribe_backend_canonico_existente(monkeypatch, caplog):
    transpiler_registry.register_transpiler_backend("python", DummyTranspiler, context="tests")
    ep = importlib.metadata.EntryPoint(
        name="python",
        value="fake.module:DummyExternalTranspiler",
        group="cobra.transpilers",
    )
    monkeypatch.setattr(
        transpiler_registry,
        "_iter_transpiler_entry_points",
        lambda: importlib.metadata.EntryPoints((ep,)),
    )
    monkeypatch.setattr(
        transpiler_registry,
        "import_module",
        lambda _name: types.SimpleNamespace(DummyExternalTranspiler=DummyTranspiler),
    )

    transpiler_registry.load_entrypoint_transpilers()

    assert dict(transpiler_registry.plugin_transpilers()) == {"python": DummyTranspiler}
    assert "ya existe en el registro canónico" in caplog.text


def test_load_entrypoint_transpilers_rechaza_clase_sin_generate_code(monkeypatch, caplog):
    class InvalidNoGenerateCode:
        pass

    ep = importlib.metadata.EntryPoint(
        name="python",
        value="fake.module:InvalidNoGenerateCode",
        group="cobra.transpilers",
    )
    monkeypatch.setattr(
        transpiler_registry,
        "_iter_transpiler_entry_points",
        lambda: importlib.metadata.EntryPoints((ep,)),
    )
    monkeypatch.setattr(
        transpiler_registry,
        "import_module",
        lambda _name: types.SimpleNamespace(InvalidNoGenerateCode=InvalidNoGenerateCode),
    )

    loaded, rejected, skipped = transpiler_registry.load_entrypoint_transpilers()

    assert (loaded, rejected, skipped) == (0, 1, 0)
    assert dict(transpiler_registry.plugin_transpilers()) == {}
    assert "no implementa el método callable 'generate_code'" in caplog.text


def test_ensure_entrypoints_loaded_once(monkeypatch):
    calls = {"load": 0}

    def _fake_load():
        calls["load"] += 1
        return (0, 0, 0)

    monkeypatch.setattr(transpiler_registry, "load_entrypoint_transpilers", _fake_load)

    transpiler_registry.ensure_entrypoint_transpilers_loaded_once()
    transpiler_registry.ensure_entrypoint_transpilers_loaded_once()

    assert calls["load"] == 1


def test_get_transpilers_overlay_plugins(monkeypatch):
    class PluginPython:
        def generate_code(self, ast):
            return "plugin"

    transpiler_registry.register_transpiler_backend("python", PluginPython, context="tests")

    merged = transpiler_registry.get_transpilers(include_plugins=True)
    official_only = transpiler_registry.get_transpilers(include_plugins=False)

    assert merged["python"] is PluginPython
    assert official_only["python"] is not PluginPython
