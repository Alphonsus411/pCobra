import pytest

from pcobra.cobra.transpilers.compatibility_matrix import BACKEND_COMPATIBILITY
from pcobra.cobra.transpilers.targets import TIER2_TARGETS
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
    support_level = BACKEND_COMPATIBILITY[backend][feature]
    if support_level == "none":
        with pytest.raises(NotImplementedError):
            generate_code(backend, feature)
        return

    generated = generate_code(backend, feature)
    assert generated.strip(), f"{backend} no generó salida para {feature}"

    if support_level == "full":
        expected_symbols = STRICT_FULL_EXPECTATIONS[backend][feature]
        for symbol in expected_symbols:
            assert symbol in generated
    elif support_level == "partial":
        expected_fallbacks = PARTIAL_EXPECTATIONS[backend][feature]
        for fallback in expected_fallbacks:
            assert fallback in generated


@pytest.mark.parametrize("backend", TIER2_BACKENDS)
@pytest.mark.parametrize("feature", HOLOBIT_FEATURES)
def test_tier2_holobit_primitives_generate_code_for_every_official_target(backend: str, feature: str):
    if BACKEND_COMPATIBILITY[backend][feature] == "none":
        with pytest.raises(NotImplementedError):
            generate_code(backend, feature)
        return

    generated = generate_code(backend, feature)
    assert generated.strip(), f"{backend} no generó código para {feature}"


@pytest.mark.parametrize("backend", TIER2_BACKENDS)
def test_tier2_core_runtime_minimum_cases_are_covered(backend: str):
    for feature in CORE_RUNTIME_FEATURES:
        generated = generate_code(backend, feature)
        assert generated.strip(), f"{backend} no generó salida para {feature}"


@pytest.mark.parametrize("backend", TIER2_BACKENDS)
def test_tier2_backend_runtime_hooks_are_present_when_expected(backend: str):
    expected_hooks = RUNTIME_HOOK_EXPECTATIONS[backend]
    if BACKEND_COMPATIBILITY[backend]["proyectar"] == "none":
        pytest.skip(f"{backend} no implementa hook de proyectar en contrato actual")

    generated = generate_code(backend, "proyectar")
    for hook in expected_hooks:
        assert hook in generated


def test_tier2_suite_targets_only_official_backends():
    assert set(TIER2_BACKENDS) == set(TIER2_TARGETS)
    assert set(TIER2_BACKENDS).issubset(set(TRANSPILERS))


def test_tier2_target_roles_remain_explicit():
    assert BACKEND_COMPATIBILITY["cpp"]["holobit"] == "partial"
    assert BACKEND_COMPATIBILITY["go"]["holobit"] == "partial"
    assert BACKEND_COMPATIBILITY["java"]["holobit"] == "partial"
    assert BACKEND_COMPATIBILITY["asm"]["holobit"] == "partial"


def test_tier2_cpp_se_mantiene_como_runtime_oficial_fuerte_y_go_java_como_adaptadores_minimos():
    cpp = generate_code("cpp", "graficar")
    go = generate_code("go", "graficar")
    java = generate_code("java", "graficar")
    asm = generate_code("asm", "graficar")

    assert "inline std::string cobra_graficar" in cpp
    assert "func cobra_graficar(hb any) string" in go
    assert "private static String cobra_graficar(Object hb)" in java
    assert "runtime de inspección/diagnóstico" in asm
