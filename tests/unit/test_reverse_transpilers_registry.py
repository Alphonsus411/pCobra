import importlib
import sys


def test_reverse_transpilers_registry_with_legacy_fallback_and_optional_dependency_logs(
    monkeypatch,
    caplog,
):
    canonical_python = "pcobra.cobra.transpilers.reverse.from_python"
    canonical_js = "pcobra.cobra.transpilers.reverse.from_js"
    canonical_go = "pcobra.cobra.transpilers.reverse.from_go"
    legacy_js = "cobra.transpilers.reverse.from_js"

    real_import_module = importlib.import_module

    def fake_import_module(name, package=None):
        if name == canonical_python:
            return real_import_module(name, package)
        if name == legacy_js:
            return real_import_module(canonical_js)
        if name == canonical_js:
            raise ModuleNotFoundError("canonical missing", name=name)
        if name == canonical_go:
            raise ModuleNotFoundError("missing optional dependency", name="tree_sitter")
        if name.startswith("pcobra.cobra.transpilers.reverse.") or name.startswith(
            "cobra.transpilers.reverse."
        ):
            raise ModuleNotFoundError("module unavailable", name=name)
        return real_import_module(name, package)

    monkeypatch.setattr(importlib, "import_module", fake_import_module)

    sys.modules.pop("pcobra.cobra.transpilers.reverse", None)

    caplog.set_level("DEBUG", logger="pcobra.cobra.transpilers.reverse")
    reverse_mod = importlib.import_module("pcobra.cobra.transpilers.reverse")

    assert "ReverseFromPython" in reverse_mod.__all__
    assert "ReverseFromJS" in reverse_mod.__all__
    assert "ReverseFromGo" not in reverse_mod.__all__

    assert any(
        "fallback legacy" in rec.message and canonical_js in rec.message and legacy_js in rec.message
        for rec in caplog.records
    )
    assert any(
        "dependencia opcional faltante" in rec.message and canonical_go in rec.message
        for rec in caplog.records
    )
