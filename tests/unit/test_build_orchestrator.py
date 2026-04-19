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


def test_build_orchestrator_preferencia_legacy_evade_metadata_invalida(monkeypatch):
    monkeypatch.setattr(
        "cobra.build.orchestrator.get_toml_map",
        lambda: {
            "modulos": {
                "demo.co": {
                    "preferred_target": "backend-invalido",
                }
            }
        },
    )

    resolution = BuildOrchestrator().resolve_backend(source_file="demo.co", preferred_backend="python")

    assert resolution.backend == "python"
