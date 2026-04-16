from cobra.build.orchestrator import BuildOrchestrator


def test_build_orchestrator_prioriza_metadata_modulo(monkeypatch):
    monkeypatch.setattr(
        "cobra.build.orchestrator.get_toml_map",
        lambda: {
            "project": {"type": "systems"},
            "modulos": {
                "demo.co": {
                    "preferred_target": "javascript",
                }
            },
        },
    )

    resolution = BuildOrchestrator().resolve_backend(source_file="demo.co")

    assert resolution.backend == "javascript"
    assert "module_target=javascript" in resolution.reason


def test_build_orchestrator_aplica_capacidad_sdk_full(monkeypatch):
    monkeypatch.setattr(
        "cobra.build.orchestrator.get_toml_map",
        lambda: {
            "project": {
                "required_capabilities": ["sdk_full"],
                "type": "web",
            }
        },
    )

    resolution = BuildOrchestrator().resolve_backend(source_file="demo.co")

    assert resolution.backend == "python"


def test_build_orchestrator_respeta_preferencia_legacy(monkeypatch):
    monkeypatch.setattr("cobra.build.orchestrator.get_toml_map", lambda: {})

    resolution = BuildOrchestrator().resolve_backend(source_file="demo.co", preferred_backend="rust")

    assert resolution.backend == "rust"
    assert "legacy" in resolution.reason


def test_build_orchestrator_bloquea_backend_legacy_en_ruta_publica(monkeypatch):
    monkeypatch.setattr("cobra.build.orchestrator.get_toml_map", lambda: {})

    try:
        BuildOrchestrator().resolve_backend(source_file="demo.co", preferred_backend="go")
    except ValueError as exc:
        assert "ruta pública" in str(exc)
        return
    raise AssertionError("Se esperaba ValueError para backend legacy en ruta pública")


def test_build_orchestrator_permite_backend_legacy_en_migracion_interna(monkeypatch):
    monkeypatch.setattr("cobra.build.orchestrator.get_toml_map", lambda: {})

    resolution = BuildOrchestrator().resolve_backend(
        source_file="demo.co",
        preferred_backend="go",
        route_scope="internal_migration",
    )

    assert resolution.backend == "go"
    assert "migración interna" in resolution.reason
