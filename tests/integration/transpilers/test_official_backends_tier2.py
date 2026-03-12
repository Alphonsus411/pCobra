import pytest

from pcobra.cobra.transpilers.compatibility_matrix import BACKEND_COMPATIBILITY
from pcobra.cobra.transpilers.targets import TIER2_TARGETS
from tests.integration.transpilers.backend_contracts import (
    FEATURE_NODES,
    PARTIAL_EXPECTATIONS,
    TRANSPILERS,
    generate_code,
)


@pytest.mark.parametrize("backend", TIER2_TARGETS)
def test_tier2_suite_covers_all_required_features(backend: str):
    for feature in FEATURE_NODES:
        generated = generate_code(backend, feature)
        assert generated.strip(), f"{backend} no generó salida para {feature}"


@pytest.mark.parametrize(
    "backend, feature",
    [(backend, feature) for backend, features in PARTIAL_EXPECTATIONS.items() if backend in TIER2_TARGETS for feature in features],
)
def test_tier2_partial_contract_requires_explicit_fallback(backend: str, feature: str):
    generated = generate_code(backend, feature)
    assert generated.strip()
    for expected_fallback in PARTIAL_EXPECTATIONS[backend][feature]:
        assert expected_fallback in generated


@pytest.mark.parametrize("backend", TIER2_TARGETS)
def test_tier2_backends_are_declared_in_contract_matrix(backend: str):
    assert backend in BACKEND_COMPATIBILITY
    assert BACKEND_COMPATIBILITY[backend]["tier"] == "tier2"


def test_tier2_suite_targets_only_official_backends():
    assert set(TIER2_TARGETS).issubset(set(TRANSPILERS))
