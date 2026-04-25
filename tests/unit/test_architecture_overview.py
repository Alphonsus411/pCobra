from pcobra.cobra.architecture.overview import (
    INTERNAL_MIGRATION_ONLY_SURFACES,
    PUBLIC_CLI_V2_COMMANDS,
    PUBLIC_FLOW_DIAGRAM,
    PUBLIC_LANGUAGE_BOUNDARY,
    USER_ROUTE_BACKEND_ENTRYPOINT,
    validate_public_architecture_overview,
)


def test_overview_declara_frontera_publica_unica():
    assert PUBLIC_LANGUAGE_BOUNDARY == "cobra"
    assert PUBLIC_CLI_V2_COMMANDS == ("run", "build", "test", "mod", "repl")
    assert USER_ROUTE_BACKEND_ENTRYPOINT == "pcobra.cobra.build.backend_pipeline"


def test_overview_marca_superficies_migracion_interna():
    assert INTERNAL_MIGRATION_ONLY_SURFACES["cli_v1"] == "internal migration only"
    assert INTERNAL_MIGRATION_ONLY_SURFACES["legacy_targets"] == "internal migration only"
    assert "bench" in INTERNAL_MIGRATION_ONLY_SURFACES["obsolete_commands"]


def test_overview_publica_diagrama_corto():
    assert "Cobra source" in PUBLIC_FLOW_DIAGRAM
    assert "AST (sin cambios)" in PUBLIC_FLOW_DIAGRAM
    assert "backend_pipeline" in PUBLIC_FLOW_DIAGRAM
    assert "runtime/binding" in PUBLIC_FLOW_DIAGRAM


def test_overview_validate_contract_no_falla():
    validate_public_architecture_overview()
