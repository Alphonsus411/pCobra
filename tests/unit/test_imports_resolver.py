from __future__ import annotations

from types import ModuleType

import pytest

from pcobra.cobra.imports.resolver import (
    CobraImportResolver,
    HybridModuleSpec,
    ImportResolutionError,
)


def test_resuelve_stdlib_antes_que_modulo_proyecto(tmp_path):
    (tmp_path / "datos.co").write_text("usar algo")
    resolver = CobraImportResolver(project_root=tmp_path)

    with pytest.warns(UserWarning, match="Colisión de import"):
        result = resolver.resolve("datos")

    assert result.source == "stdlib"
    assert result.resolved_name == "cobra.datos"


def test_prefiere_namespace_explicito_cobra_datos():
    resolver = CobraImportResolver()

    result = resolver.resolve("cobra.datos")

    assert result.source == "stdlib"
    assert result.import_path == "pcobra.standard_library.datos"


def test_colision_stdlib_vs_bridge_genera_warning(monkeypatch):
    resolver = CobraImportResolver()

    import importlib.util

    original_find_spec = importlib.util.find_spec

    def fake_find_spec(name: str):
        if name == "datos":
            class DummySpec:
                loader = object()

            return DummySpec()
        return original_find_spec(name)

    monkeypatch.setattr(importlib.util, "find_spec", fake_find_spec)

    with pytest.warns(UserWarning, match="Colisión de import"):
        result = resolver.resolve("datos")

    assert result.source == "stdlib"


def test_colision_en_modo_estricto_falla(tmp_path):
    (tmp_path / "datos.co").write_text("usar algo")
    resolver = CobraImportResolver(project_root=tmp_path, strict_ambiguous_imports=True)

    with pytest.raises(ImportResolutionError, match="strict mode"):
        resolver.resolve("datos")


def test_bridge_python_directo():
    resolver = CobraImportResolver()

    result = resolver.resolve("json")

    assert result.source == "python_bridge"
    assert result.import_path == "json"


def test_modulo_hibrido_inyecta_adapter_backend(monkeypatch):
    fake_module = ModuleType("mi_hibrido_runtime")

    import importlib

    original_import_module = importlib.import_module

    def fake_import_module(name: str):
        if name == "mi_hibrido_runtime":
            return fake_module
        return original_import_module(name)

    monkeypatch.setattr(importlib, "import_module", fake_import_module)

    resolver = CobraImportResolver(
        hybrid_modules={
            "mi_hibrido": HybridModuleSpec(
                module="mi_hibrido",
                import_path="mi_hibrido_runtime",
                backend="javascript",
            )
        }
    )

    resolution, module = resolver.load_module("mi_hibrido", fallback_backend="python")

    assert resolution.source == "hybrid"
    assert module is fake_module
    assert getattr(module, "__cobra_backend__") == "javascript"
    assert getattr(module, "__cobra_backend_adapter__").__class__.__name__ == "JavaScriptAdapter"
    assert getattr(module, "__cobra_resolution_source__") == "hybrid"
    assert getattr(module, "__cobra_backend_injected__") == "javascript"
    assert getattr(module, "__cobra_resolution_metadata__") == {
        "request": "mi_hibrido",
        "source": "hybrid",
        "resolved_name": "mi_hibrido",
        "backend": "javascript",
        "import_path": "mi_hibrido_runtime",
    }


def test_resolver_adjunta_adapter_desde_resolucion():
    resolver = CobraImportResolver()

    result = resolver.resolve("json")

    assert result.backend is not None
    assert result.backend_adapter is not None


def test_error_si_no_hay_candidato():
    resolver = CobraImportResolver()

    with pytest.raises(ImportResolutionError):
        resolver.resolve("__modulo_improbable_no_existente__")
