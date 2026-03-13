import pytest

from pcobra.cobra.transpilers.compatibility_matrix import BACKEND_COMPATIBILITY
from pcobra.cobra.transpilers.targets import TIER1_TARGETS
from tests.integration.transpilers.backend_contracts import (
    CORE_RUNTIME_FEATURES,
    HOLOBIT_FEATURES,
    PARTIAL_EXPECTATIONS,
    REQUIRED_FEATURES,
    RUNTIME_HOOK_EXPECTATIONS,
    STRICT_FULL_EXPECTATIONS,
    TRANSPILERS,
    generate_code,
)


TIER1_BACKENDS = tuple(backend for backend in TIER1_TARGETS if BACKEND_COMPATIBILITY.get(backend, {}).get("tier") == "tier1")


@pytest.mark.parametrize("backend", TIER1_BACKENDS)
def test_tier1_matrix_declares_minimum_battery_for_every_target(backend: str):
    declared = BACKEND_COMPATIBILITY[backend]
    for feature in REQUIRED_FEATURES:
        assert declared.get(feature) in {"full", "partial", "none"}


@pytest.mark.parametrize(
    "backend, feature",
    [(backend, feature) for backend in TIER1_BACKENDS for feature in REQUIRED_FEATURES],
)
def test_tier1_backend_contract_matches_compatibility_matrix(backend: str, feature: str):
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


@pytest.mark.parametrize("backend", TIER1_BACKENDS)
@pytest.mark.parametrize("feature", HOLOBIT_FEATURES)
def test_tier1_holobit_primitives_generate_code_for_every_official_target(backend: str, feature: str):
    generated = generate_code(backend, feature)
    assert generated.strip(), f"{backend} no generó código para {feature}"


@pytest.mark.parametrize("backend", TIER1_BACKENDS)
def test_tier1_core_runtime_minimum_cases_are_covered(backend: str):
    for feature in CORE_RUNTIME_FEATURES:
        generated = generate_code(backend, feature)
        assert generated.strip(), f"{backend} no generó salida para {feature}"


@pytest.mark.parametrize("backend", TIER1_BACKENDS)
def test_tier1_backend_runtime_hooks_are_present_when_expected(backend: str):
    expected_hooks = RUNTIME_HOOK_EXPECTATIONS[backend]
    if not expected_hooks:
        pytest.skip(f"{backend} no define hooks runtime dedicados para este contrato")

    generated = generate_code(backend, "proyectar")
    for hook in expected_hooks:
        assert hook in generated


def test_tier1_suite_targets_only_official_backends():
    assert set(TIER1_BACKENDS) == set(TIER1_TARGETS)
    assert set(TIER1_BACKENDS).issubset(set(TRANSPILERS))
