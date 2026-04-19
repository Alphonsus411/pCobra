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


def test_build_orchestrator_permite_backend_internal_only_con_flag(monkeypatch):
    monkeypatch.setattr("cobra.build.orchestrator.get_toml_map", lambda: {})
    monkeypatch.setenv("COBRA_INTERNAL_LEGACY_TARGETS", "1")

    resolution = BuildOrchestrator().resolve_backend(source_file="demo.co", preferred_backend="go")

    assert resolution.backend == "go"
    assert "legacy" in resolution.reason


def test_build_orchestrator_rechaza_backend_internal_only_sin_flag(monkeypatch):
    monkeypatch.setattr("cobra.build.orchestrator.get_toml_map", lambda: {})
    monkeypatch.delenv("COBRA_INTERNAL_LEGACY_TARGETS", raising=False)

    try:
        BuildOrchestrator().resolve_backend(source_file="demo.co", preferred_backend="go")
    except ValueError as exc:
        error = str(exc)
    else:
        raise AssertionError("Se esperaba ValueError para backend internal-only sin flag")

    assert "Backend no permitido" in error
    assert "go" not in error.split("Permitidos: ", 1)[-1]
