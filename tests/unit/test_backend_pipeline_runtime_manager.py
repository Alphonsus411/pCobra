from pcobra.cobra.build import backend_pipeline


class _DummyTranspiler:
    def generate_code(self, ast):
        return f"code:{len(ast)}"


def test_backend_pipeline_build_expone_contexto_runtime(monkeypatch):
    monkeypatch.setattr(
        backend_pipeline,
        "resolve_backend_runtime",
        lambda source, hints=None: (
            type("R", (), {"backend": "python", "reason": "test"})(),
            {
                "language": "python",
                "route": "python_direct_import",
                "bridge": "python_direct_bridge",
                "security_profile": "same_process_safe_mode",
                "abi_contract": "Contrato Python estable por API pública y typing",
                "abi_version": "1.0",
            },
        ),
    )
    monkeypatch.setattr(backend_pipeline, "obtener_ast", lambda _codigo: ["ast"])
    monkeypatch.setattr(backend_pipeline, "_official_transpilers", lambda: {"python": _DummyTranspiler})

    result = backend_pipeline.build("imprimir(1)", hints={"preferred_backend": "python"})

    assert result["backend"] == "python"
    assert result["reason"] is None
    assert result["runtime"]["abi_version"] == "1.0"
    assert result["runtime"]["route"] == "python_direct_import"


def test_backend_pipeline_build_expone_reason_solo_en_debug(monkeypatch):
    monkeypatch.setattr(
        backend_pipeline,
        "resolve_backend_runtime",
        lambda source, hints=None: (
            type("R", (), {"backend": "python", "reason": "debug-reason"})(),
            {
                "language": "python",
                "route": "python_direct_import",
                "bridge": "python_direct_bridge",
                "security_profile": "same_process_safe_mode",
                "abi_contract": "Contrato Python estable por API pública y typing",
                "abi_version": "1.0",
            },
        ),
    )
    monkeypatch.setattr(backend_pipeline, "obtener_ast", lambda _codigo: ["ast"])
    monkeypatch.setattr(backend_pipeline, "_official_transpilers", lambda: {"python": _DummyTranspiler})

    result = backend_pipeline.build("imprimir(1)", hints={"preferred_backend": "python", "debug": True})

    assert result["reason"] == "debug-reason"


def test_backend_pipeline_resolve_backend_envia_scope_migracion(monkeypatch):
    captured = {}

    def _fake_resolve_backend(self, *, source_file, preferred_backend, required_capabilities, route_scope):
        captured["route_scope"] = route_scope
        return type("R", (), {"backend": "go", "reason": "migration"})()

    monkeypatch.setattr(backend_pipeline, "ORCHESTRATOR", type("O", (), {"resolve_backend": _fake_resolve_backend})())

    backend_pipeline.resolve_backend(
        "demo.co",
        {"preferred_backend": "go", "internal_migration": True},
    )

    assert captured["route_scope"] == "internal_migration"
