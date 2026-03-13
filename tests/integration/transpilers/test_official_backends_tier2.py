import pytest

from pcobra.cobra.transpilers.compatibility_matrix import BACKEND_COMPATIBILITY
from pcobra.cobra.transpilers.targets import TIER2_TARGETS
from tests.integration.transpilers.backend_contracts import (
    PARTIAL_EXPECTATIONS,
    REQUIRED_FEATURES,
    STRICT_FULL_EXPECTATIONS,
    TRANSPILERS,
    generate_code,
)


TIER2_BACKENDS = tuple(backend for backend in TIER2_TARGETS if BACKEND_COMPATIBILITY.get(backend, {}).get("tier") == "tier2")


@pytest.mark.parametrize("backend", TIER2_BACKENDS)
def test_tier2_matrix_declares_minimum_battery_for_every_target(backend: str):
    declared = BACKEND_COMPATIBILITY[backend]
    for feature in REQUIRED_FEATURES:
        assert declared.get(feature) in {"full", "partial", "none"}


@pytest.mark.parametrize(
    "backend, feature",
    [(backend, feature) for backend in TIER2_BACKENDS for feature in REQUIRED_FEATURES],
)
def test_tier2_backend_contract_matches_compatibility_matrix(backend: str, feature: str):
    generated = generate_code(backend, feature)
    assert generated.strip(), f"{backend} no generó salida para {feature}"

    support_level = BACKEND_COMPATIBILITY[backend][feature]
    if support_level == "full":
        expected_symbols = STRICT_FULL_EXPECTATIONS[backend][feature]
        for symbol in expected_symbols:
            assert symbol in generated
    elif support_level == "partial":
        expected_fallbacks = PARTIAL_EXPECTATIONS[backend][feature]
        for fallback in expected_fallbacks:
            assert fallback in generated


def test_tier2_suite_targets_only_official_backends():
    assert set(TIER2_BACKENDS) == set(TIER2_TARGETS)
    assert set(TIER2_BACKENDS).issubset(set(TRANSPILERS))
