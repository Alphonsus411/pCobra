import importlib.metadata
import types

import pytest

from pcobra.cobra.cli.commands import compile_cmd


class DummyTranspiler:
    pass


def test_register_transpiler_backend_rechaza_backend_no_oficial(monkeypatch):
    monkeypatch.setattr(compile_cmd, "TRANSPILERS", {})

    with pytest.raises(
        ValueError, match=r"Backend no permitido en tests: backend_no_soportado"
    ):
        compile_cmd.register_transpiler_backend(
            "backend_no_soportado", DummyTranspiler, context="tests"
        )


def test_register_transpiler_backend_normaliza_alias_y_registra(monkeypatch):
    monkeypatch.setattr(compile_cmd, "TRANSPILERS", {})

    canonical = compile_cmd.register_transpiler_backend("js", DummyTranspiler, context="tests")

    assert canonical == "javascript"
    assert compile_cmd.TRANSPILERS["javascript"] is DummyTranspiler


def test_validate_entrypoint_backend_rechaza_alias_legacy():
    with pytest.raises(
        ValueError,
        match=r"entry points solo pueden usar nombres canónicos oficiales",
    ):
        compile_cmd._validate_entrypoint_backend_or_raise("js", context="tests")


def test_load_entrypoint_transpilers_omite_backend_no_canonico(monkeypatch, caplog):
    ep = importlib.metadata.EntryPoint(
        name="js",
        value="tests.unit.test_compile_backend_registration:DummyTranspiler",
        group="cobra.transpilers",
    )
    monkeypatch.setattr(compile_cmd, "TRANSPILERS", {})
    monkeypatch.setattr(
        compile_cmd,
        "_iter_transpiler_entry_points",
        lambda: importlib.metadata.EntryPoints((ep,)),
    )

    compile_cmd.load_entrypoint_transpilers()

    assert compile_cmd.TRANSPILERS == {}
    assert "omitido: target no oficial/no canónico" in caplog.text


def test_load_entrypoint_transpilers_registra_backend_canonico(monkeypatch):
    ep = importlib.metadata.EntryPoint(
        name="python",
        value="fake.module:DummyExternalTranspiler",
        group="cobra.transpilers",
    )
    monkeypatch.setattr(compile_cmd, "TRANSPILERS", {})
    monkeypatch.setattr(
        compile_cmd,
        "_iter_transpiler_entry_points",
        lambda: importlib.metadata.EntryPoints((ep,)),
    )
    monkeypatch.setattr(
        compile_cmd,
        "import_module",
        lambda _name: types.SimpleNamespace(DummyExternalTranspiler=DummyTranspiler),
    )

    compile_cmd.load_entrypoint_transpilers()

    assert compile_cmd.TRANSPILERS == {"python": DummyTranspiler}
