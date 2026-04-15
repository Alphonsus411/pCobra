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
    monkeypatch.setattr(backend_pipeline, "TRANSPILERS", {"python": _DummyTranspiler})

    result = backend_pipeline.build("imprimir(1)", mode="python")

    assert result["backend"] == "python"
    assert result["runtime"]["abi_version"] == "1.0"
    assert result["runtime"]["route"] == "python_direct_import"
