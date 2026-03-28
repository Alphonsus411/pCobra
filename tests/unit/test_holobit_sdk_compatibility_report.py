from __future__ import annotations

from pathlib import Path

import pytest

from pcobra.cobra.transpilers.compatibility_matrix import (
    BACKEND_HOLOBIT_SDK_CAPABILITIES,
    CRITICAL_HOLOBIT_CAPABILITIES,
    HOLOBIT_CAPABILITY_FALLBACKS,
    HOLOBIT_SDK_CAPABILITIES,
    MIN_REQUIRED_TIER1_HOLOBIT_CAPABILITIES,
    VALID_HOLOBIT_CAPABILITY_STATUSES,
    validate_tier1_holobit_release_gate,
)
from pcobra.cobra.transpilers.common.utils import get_runtime_hooks
from pcobra.cobra.transpilers.targets import OFFICIAL_TARGETS, TIER1_TARGETS

DOC_PATH = Path("docs/compatibility/holobit-sdk.md")


@pytest.mark.parametrize("backend", OFFICIAL_TARGETS)
def test_holobit_sdk_capabilities_shape_and_statuses_by_target(backend: str) -> None:
    capabilities = BACKEND_HOLOBIT_SDK_CAPABILITIES[backend]
    assert set(capabilities) == set(HOLOBIT_SDK_CAPABILITIES)
    for capability in HOLOBIT_SDK_CAPABILITIES:
        assert capabilities[capability] in VALID_HOLOBIT_CAPABILITY_STATUSES


@pytest.mark.parametrize("backend", OFFICIAL_TARGETS)
def test_holobit_sdk_smoke_import_hooks_present_in_runtime_hooks(backend: str) -> None:
    hook_blob = "\n".join(get_runtime_hooks(backend))
    assert "cobra_holobit" in hook_blob
    assert "cobra_proyectar" in hook_blob
    assert "cobra_transformar" in hook_blob
    assert "cobra_graficar" in hook_blob


@pytest.mark.parametrize("backend", OFFICIAL_TARGETS)
@pytest.mark.parametrize("capability", HOLOBIT_SDK_CAPABILITIES)
def test_holobit_sdk_has_explicit_limitation_or_fallback_for_every_capability(
    backend: str,
    capability: str,
) -> None:
    fallback = HOLOBIT_CAPABILITY_FALLBACKS[backend][capability]
    assert isinstance(fallback, str)
    assert fallback.strip()


@pytest.mark.parametrize("backend", TIER1_TARGETS)
@pytest.mark.parametrize("capability", CRITICAL_HOLOBIT_CAPABILITIES)
def test_tier1_critical_holobit_capabilities_do_not_regress_below_minimum(
    backend: str,
    capability: str,
) -> None:
    current = BACKEND_HOLOBIT_SDK_CAPABILITIES[backend][capability]
    minimum = MIN_REQUIRED_TIER1_HOLOBIT_CAPABILITIES[backend][capability]

    order = {"none": 0, "partial": 1, "full": 2}
    assert order[current] >= order[minimum]


def test_holobit_sdk_compatibility_report_exists_and_contains_matrix_and_gate() -> None:
    content = DOC_PATH.read_text(encoding="utf-8")

    assert "Compatibilidad Holobit SDK" in content
    assert "| Target | Tier | Runtime | Serialización | IPC | Módulos nativos | Import hooks | Estado general |" in content
    assert "`python`" in content
    assert "`javascript`" in content
    assert "`rust`" in content
    assert "`wasm`" in content
    assert "`go`" in content
    assert "`cpp`" in content
    assert "`java`" in content
    assert "`asm`" in content
    lowered = content.lower()
    assert "release" in lowered
    assert "bloque" in lowered


def test_release_gate_fails_if_tier1_breaks_critical_holobit_capability() -> None:
    regressed = {
        backend: dict(capabilities)
        for backend, capabilities in BACKEND_HOLOBIT_SDK_CAPABILITIES.items()
    }
    regressed["rust"]["runtime"] = "none"

    with pytest.raises(RuntimeError, match="Regresión crítica Holobit en Tier 1"):
        validate_tier1_holobit_release_gate(regressed)
