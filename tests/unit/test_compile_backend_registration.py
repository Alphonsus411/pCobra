import importlib.metadata
import types

import pytest

from pcobra.cobra.cli.commands import compile_cmd


class DummyTranspiler:
    pass


def test_register_transpiler_backend_rechaza_backend_no_oficial(monkeypatch):
    monkeypatch.setattr(compile_cmd, "TRANSPILERS", {})

    with pytest.raises(
        ValueError, match=r"Target no soportado: 'backend_no_soportado'"
    ):
        compile_cmd.register_transpiler_backend(
            "backend_no_soportado", DummyTranspiler, context="tests"
        )


def test_register_transpiler_backend_acepta_backend_canonico(monkeypatch):
    monkeypatch.setattr(compile_cmd, "TRANSPILERS", {})

    canonical = compile_cmd.register_transpiler_backend("javascript", DummyTranspiler, context="tests")

    assert canonical == "javascript"
    assert compile_cmd.TRANSPILERS["javascript"] is DummyTranspiler


def test_validate_entrypoint_backend_rechaza_backend_fuera_del_set_oficial():
    with pytest.raises(
        ValueError,
        match=r"Target no soportado: 'fantasy'",
    ):
        compile_cmd._validate_entrypoint_backend_or_raise("fantasy", context="tests")


def test_load_entrypoint_transpilers_omite_backend_fuera_del_set_oficial(monkeypatch, caplog):
    ep = importlib.metadata.EntryPoint(
        name="fantasy",
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
    assert "rechazado por política oficial" in caplog.text
    assert "Target no soportado: 'fantasy'" in caplog.text


def test_load_entrypoint_transpilers_rechaza_alias_no_canonico(monkeypatch, caplog):
    ep = importlib.metadata.EntryPoint(
        name="c++",
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
    assert "rechazado por política oficial" in caplog.text
    assert "c++" in caplog.text


@pytest.mark.parametrize("legacy_backend", ("j" "s", "as" "sembly", "nodejs", "python3"))
def test_load_entrypoint_transpilers_rechaza_backends_legacy_o_ambiguos(monkeypatch, caplog, legacy_backend):
    ep = importlib.metadata.EntryPoint(
        name=legacy_backend,
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
    assert "rechazado por política oficial" in caplog.text
    assert "legacy/ambiguo" in caplog.text


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


def test_load_entrypoint_transpilers_no_sobrescribe_backend_canonico_existente(monkeypatch, caplog):
    ep = importlib.metadata.EntryPoint(
        name="python",
        value="fake.module:DummyExternalTranspiler",
        group="cobra.transpilers",
    )
    monkeypatch.setattr(compile_cmd, "TRANSPILERS", {"python": object})
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

    assert compile_cmd.TRANSPILERS == {"python": object}
    assert "ya existe en el registro canónico" in caplog.text
