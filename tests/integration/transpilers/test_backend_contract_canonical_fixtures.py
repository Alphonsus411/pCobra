from __future__ import annotations

import pytest

from pcobra.cobra.transpilers.compatibility_matrix import BACKEND_COMPATIBILITY, CONTRACT_FEATURES
from pcobra.cobra.transpilers.targets import OFFICIAL_TARGETS
from tests.integration.transpilers.backend_contracts import (
    CANONICAL_FULL_PROGRAM_FIXTURE,
    CANONICAL_PROGRAM_FIXTURES,
    PARTIAL_CONTRACT_ERROR_MARKERS,
    PARTIAL_EXPECTATIONS,
    STRICT_FULL_EXPECTATIONS,
    generate_code,
)


def test_canonical_fixtures_cover_required_contract_features():
    assert tuple(CANONICAL_PROGRAM_FIXTURES) == tuple(CONTRACT_FEATURES)
    for feature, fixture in CANONICAL_PROGRAM_FIXTURES.items():
        source = str(fixture["source"])
        nodes = fixture["nodes"]
        assert source.strip(), f"fixture sin source para feature={feature}"
        assert nodes, f"fixture sin nodos para feature={feature}"

    full_source = str(CANONICAL_FULL_PROGRAM_FIXTURE["source"])
    assert "holobit" in full_source
    assert "proyectar" in full_source
    assert "transformar" in full_source
    assert "graficar" in full_source
    assert "usar corelibs" in full_source
    assert "usar standard_library" in full_source


@pytest.mark.parametrize("feature", CONTRACT_FEATURES)
def test_python_backend_is_full_for_every_contract_feature(feature: str):
    assert BACKEND_COMPATIBILITY["python"][feature] == "full"
    generated = generate_code("python", feature)
    for marker in STRICT_FULL_EXPECTATIONS["python"][feature]:
        assert marker in generated


@pytest.mark.parametrize(
    "backend",
    tuple(target for target in OFFICIAL_TARGETS if target != "python"),
)
def test_non_python_backends_respect_declared_contract_feature_levels(backend: str):
    for feature in CONTRACT_FEATURES:
        assert BACKEND_COMPATIBILITY[backend][feature] in {"partial", "full"}
        generated = generate_code(backend, feature)
        assert generated.strip(), f"{backend} no generó salida para {feature}"
        for marker in PARTIAL_EXPECTATIONS[backend][feature]:
            assert marker in generated


@pytest.mark.parametrize("backend", tuple(PARTIAL_CONTRACT_ERROR_MARKERS))
@pytest.mark.parametrize("feature", ("proyectar", "transformar", "graficar"))
def test_partial_contract_error_messages_are_stable_and_verifiable(backend: str, feature: str):
    generated = generate_code(backend, feature)
    for marker in PARTIAL_CONTRACT_ERROR_MARKERS[backend][feature]:
        assert marker in generated
