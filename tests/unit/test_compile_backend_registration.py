import pytest

from pcobra.cobra.cli.commands import compile_cmd


class DummyTranspiler:
    pass


def test_register_transpiler_backend_rechaza_backend_no_oficial(monkeypatch):
    monkeypatch.setattr(compile_cmd, "TRANSPILERS", {})

    with pytest.raises(ValueError, match=r"Backend no permitido en tests: ruby"):
        compile_cmd.register_transpiler_backend("ruby", DummyTranspiler, context="tests")


def test_register_transpiler_backend_normaliza_alias_y_registra(monkeypatch):
    monkeypatch.setattr(compile_cmd, "TRANSPILERS", {})

    canonical = compile_cmd.register_transpiler_backend("js", DummyTranspiler, context="tests")

    assert canonical == "javascript"
    assert compile_cmd.TRANSPILERS["javascript"] is DummyTranspiler
