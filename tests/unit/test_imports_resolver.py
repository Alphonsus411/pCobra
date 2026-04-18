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
    resolver = CobraImportResolver(project_root=tmp_path, collision_policy="warn")

    with pytest.warns(UserWarning, match="Colisión de import"):
        result = resolver.resolve("datos")

    assert result.source == "stdlib"
    assert result.resolved_name == "cobra.datos"


def test_prefiere_namespace_explicito_cobra_datos():
    resolver = CobraImportResolver(collision_policy="warn")

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


def test_colision_stdlib_proyecto_y_bridge_respeta_orden(monkeypatch, tmp_path):
    (tmp_path / "datos.co").write_text("usar algo")
    resolver = CobraImportResolver(project_root=tmp_path, collision_policy="warn")

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
    assert result.resolved_name == "cobra.datos"
    assert result.precedence_reason == "source_order:stdlib > project > python_bridge > hybrid"


def test_colision_total_namespace_required_falla(monkeypatch, tmp_path):
    (tmp_path / "datos.co").write_text("usar algo")
    resolver = CobraImportResolver(project_root=tmp_path, collision_policy="namespace_required")

    import importlib.util

    original_find_spec = importlib.util.find_spec

    def fake_find_spec(name: str):
        if name == "datos":
            class DummySpec:
                loader = object()

            return DummySpec()
        return original_find_spec(name)

    monkeypatch.setattr(importlib.util, "find_spec", fake_find_spec)

    with pytest.raises(ImportResolutionError, match="namespace_required"):
        resolver.resolve("datos")


def test_colision_en_modo_estricto_falla(tmp_path):
    (tmp_path / "datos.co").write_text("usar algo")
    resolver = CobraImportResolver(project_root=tmp_path, strict_ambiguous_imports=True)

    with pytest.raises(ImportResolutionError, match="strict mode"):
        resolver.resolve("datos")


def test_colision_en_namespace_required_falla(tmp_path):
    (tmp_path / "datos.co").write_text("usar algo")
    resolver = CobraImportResolver(project_root=tmp_path, collision_policy="namespace_required")

    with pytest.raises(ImportResolutionError, match="namespace_required"):
        resolver.resolve("datos")


def test_politica_colisiones_desde_config(monkeypatch, tmp_path):
    (tmp_path / "datos.co").write_text("usar algo")
    monkeypatch.setattr(
        "pcobra.cobra.imports.resolver.get_toml_map",
        lambda: {"imports": {"collision_policy": "strict_error"}},
    )
    resolver = CobraImportResolver(project_root=tmp_path)

    with pytest.raises(ImportResolutionError, match="strict mode"):
        resolver.resolve("datos")


def test_bridge_python_directo():
    resolver = CobraImportResolver()

    result = resolver.resolve("json")

    assert result.source == "python_bridge"
    assert result.import_path == "json"


def test_ruta_oficial_importar_pandas_via_python_bridge(monkeypatch):
    resolver = CobraImportResolver()

    import importlib.util

    original_find_spec = importlib.util.find_spec

    def fake_find_spec(name: str):
        if name == "pandas":
            class DummySpec:
                loader = object()

            return DummySpec()
        return original_find_spec(name)

    monkeypatch.setattr(importlib.util, "find_spec", fake_find_spec)

    result = resolver.resolve("pandas")

    assert result.source == "python_bridge"
    assert result.resolved_name == "pandas"


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
        "api_contract_version": "2026-04-import-resolution-v1",
        "resolution_source_order": ["stdlib", "project", "python_bridge", "hybrid"],
        "collision_policy": "namespace_required",
        "request": "mi_hibrido",
        "source": "hybrid",
        "resolved_name": "mi_hibrido",
        "backend": "javascript",
        "import_path": "mi_hibrido_runtime",
        "precedence_reason": "unique_source:hybrid",
        "audit_debug": False,
    }


def test_modulo_hibrido_desde_config(monkeypatch):
    fake_module = ModuleType("hibrido_config_runtime")

    import importlib

    original_import_module = importlib.import_module

    def fake_import_module(name: str):
        if name == "hibrido_config_runtime":
            return fake_module
        return original_import_module(name)

    monkeypatch.setattr(importlib, "import_module", fake_import_module)
    monkeypatch.setattr(
        "pcobra.cobra.imports.resolver.get_toml_map",
        lambda: {
            "imports": {
                "hybrid_modules": {
                    "mod_hibrido": {
                        "import_path": "hibrido_config_runtime",
                        "backend": "python",
                    }
                }
            }
        },
    )
    resolver = CobraImportResolver()

    resolution, module = resolver.load_module("mod_hibrido")

    assert resolution.source == "hybrid"
    assert module is fake_module


def test_metadata_uniforme_en_ruta_stdlib():
    resolver = CobraImportResolver()

    resolution, module = resolver.load_module("cobra.datos")

    assert resolution.source == "stdlib"
    assert module is not None
    metadata = getattr(module, "__cobra_resolution_metadata__")
    assert metadata["source"] == "stdlib"
    assert metadata["api_contract_version"] == "2026-04-import-resolution-v1"
    assert metadata["resolution_source_order"] == ["stdlib", "project", "python_bridge", "hybrid"]
    assert metadata["collision_policy"] == "namespace_required"
    assert metadata["audit_debug"] is False


def test_metadata_uniforme_en_ruta_python_bridge():
    resolver = CobraImportResolver()

    resolution, module = resolver.load_module("json")

    assert resolution.source == "python_bridge"
    assert module is not None
    metadata = getattr(module, "__cobra_resolution_metadata__")
    assert metadata["source"] == "python_bridge"
    assert metadata["api_contract_version"] == "2026-04-import-resolution-v1"
    assert metadata["resolution_source_order"] == ["stdlib", "project", "python_bridge", "hybrid"]
    assert metadata["collision_policy"] == "namespace_required"
    assert metadata["audit_debug"] is False


def test_resolver_adjunta_adapter_desde_resolucion():
    resolver = CobraImportResolver()

    result = resolver.resolve("json")

    assert result.backend is not None
    assert result.backend_adapter is not None
    assert result.precedence_reason == "unique_source:python_bridge"


def test_resolver_usa_contrato_publico_para_backend_stdlib():
    resolver = CobraImportResolver()

    result = resolver.resolve("cobra.web")

    assert result.source == "stdlib"
    assert result.backend == "javascript"
    assert result.backend_adapter is not None


def test_modo_migracion_habilita_warn_desde_config(monkeypatch, tmp_path):
    (tmp_path / "datos.co").write_text("usar algo")
    monkeypatch.setattr(
        "pcobra.cobra.imports.resolver.get_toml_map",
        lambda: {"imports": {"migration_mode": True}},
    )
    resolver = CobraImportResolver(project_root=tmp_path)

    with pytest.warns(UserWarning, match="Colisión de import"):
        result = resolver.resolve("datos")

    assert result.source == "stdlib"
    assert resolver.collision_policy == "warn"


def test_colision_short_import_namespace_required_incluye_recomendacion(tmp_path):
    (tmp_path / "datos.co").write_text("usar algo")
    resolver = CobraImportResolver(project_root=tmp_path)

    with pytest.raises(ImportResolutionError) as excinfo:
        resolver.resolve("datos")

    message = str(excinfo.value)
    assert "cobra.datos" in message
    assert "app.datos" in message
    assert "importar datos" in message


def test_import_namespaced_no_colision_con_modulo_local(tmp_path):
    app_dir = tmp_path / "app"
    app_dir.mkdir()
    (app_dir / "datos.co").write_text("usar algo")
    resolver = CobraImportResolver(project_root=tmp_path)

    stdlib_result = resolver.resolve("cobra.datos")
    project_result = resolver.resolve("app.datos")

    assert stdlib_result.source == "stdlib"
    assert project_result.source == "project"


def test_load_module_inyecta_backend_adapter_en_ruta_namespaced_stdlib():
    resolver = CobraImportResolver()

    _, module = resolver.load_module("cobra.datos")

    assert module is not None
    assert getattr(module, "__cobra_backend_adapter__", None) is not None


def test_motivo_precedencia_en_colision(tmp_path):
    (tmp_path / "datos.co").write_text("usar algo")
    resolver = CobraImportResolver(project_root=tmp_path, collision_policy="warn")

    with pytest.warns(UserWarning, match="Colisión de import"):
        result = resolver.resolve("datos")

    assert result.precedence_reason == "source_order:stdlib > project > python_bridge > hybrid"


def test_error_si_no_hay_candidato():
    resolver = CobraImportResolver()

    with pytest.raises(ImportResolutionError):
        resolver.resolve("__modulo_improbable_no_existente__")


def test_error_colision_expone_codigo_estable(tmp_path):
    (tmp_path / "datos.co").write_text("usar algo")
    resolver = CobraImportResolver(project_root=tmp_path)

    with pytest.raises(ImportResolutionError) as excinfo:
        resolver.resolve("datos")

    assert excinfo.value.code == "IMP-COLLISION-001"
    assert "[IMP-COLLISION-001]" in str(excinfo.value)


def test_audit_debug_registra_resolucion_y_precedence_reason(tmp_path):
    (tmp_path / "datos.co").write_text("usar algo")
    resolver = CobraImportResolver(
        project_root=tmp_path,
        collision_policy="warn",
        audit_debug=True,
    )

    with pytest.warns(UserWarning, match="Colisión de import"):
        resolver.resolve("datos")

    assert len(resolver.audit_events) == 1
    event = resolver.audit_events[0]
    assert event.request == "datos"
    assert event.source == "stdlib"
    assert event.precedence_reason == "source_order:stdlib > project > python_bridge > hybrid"


def test_resolver_expone_estabilidad_de_orden_en_major():
    assert CobraImportResolver.resolution_source_order == (
        "stdlib",
        "project",
        "python_bridge",
        "hybrid",
    )
    assert CobraImportResolver.resolution_source_order_stability == "major"

