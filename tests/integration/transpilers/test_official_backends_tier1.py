import pytest

from pcobra.cobra.transpilers.compatibility_matrix import BACKEND_COMPATIBILITY
from pcobra.cobra.transpilers.targets import TIER1_TARGETS
from tests.integration.transpilers.backend_contracts import (
    FEATURE_NODES,
    PARTIAL_EXPECTATIONS,
    STRICT_FULL_EXPECTATIONS,
    TRANSPILERS,
    generate_code,
)


@pytest.mark.parametrize("backend", TIER1_TARGETS)
def test_tier1_suite_covers_all_required_features(backend: str):
    for feature in FEATURE_NODES:
        generated = generate_code(backend, feature)
        assert generated.strip(), f"{backend} no generó salida para {feature}"


@pytest.mark.parametrize(
    "backend, feature",
    [(backend, feature) for backend, features in STRICT_FULL_EXPECTATIONS.items() if backend in TIER1_TARGETS for feature in features],
)
def test_tier1_full_contract_is_strict(backend: str, feature: str):
    generated = generate_code(backend, feature)
    for expected_symbol in STRICT_FULL_EXPECTATIONS[backend][feature]:
        assert expected_symbol in generated


@pytest.mark.parametrize(
    "backend, feature",
    [(backend, feature) for backend, features in PARTIAL_EXPECTATIONS.items() if backend in TIER1_TARGETS for feature in features],
)
def test_tier1_partial_contract_requires_explicit_fallback(backend: str, feature: str):
    generated = generate_code(backend, feature)
    assert generated.strip()
    for expected_fallback in PARTIAL_EXPECTATIONS[backend][feature]:
        assert expected_fallback in generated


@pytest.mark.parametrize("backend", TIER1_TARGETS)
def test_tier1_backends_are_declared_in_contract_matrix(backend: str):
    assert backend in BACKEND_COMPATIBILITY
    assert BACKEND_COMPATIBILITY[backend]["tier"] == "tier1"


def test_tier1_suite_targets_only_official_backends():
    assert set(TIER1_TARGETS).issubset(set(TRANSPILERS))
