"""Constantes y helpers compartidos de targets soportados para la suite de tests."""

from __future__ import annotations

from typing import Iterable, Literal

from pcobra.cobra.cli.target_policies import (
    BEST_EFFORT_RUNTIME_TARGETS,
    NO_RUNTIME_TARGETS,
    OFFICIAL_RUNTIME_TARGETS,
    OFFICIAL_TRANSPILATION_TARGETS,
    TRANSPILATION_ONLY_TARGETS,
    VERIFICATION_EXECUTABLE_TARGETS,
)
from pcobra.cobra.transpilers.compatibility_matrix import BACKEND_COMPATIBILITY
from pcobra.cobra.transpilers.targets import OFFICIAL_TARGETS, TIER1_TARGETS, TIER2_TARGETS

TierName = Literal["tier1", "tier2"]

SUPPORTED_TARGETS = OFFICIAL_TARGETS
OFFICIAL_TRANSPILATION_TARGETS_IN_TESTS = OFFICIAL_TRANSPILATION_TARGETS
TIER1_SUPPORTED_TARGETS = TIER1_TARGETS
TIER2_SUPPORTED_TARGETS = TIER2_TARGETS
BEST_EFFORT_INTERNAL_RUNTIME_TARGETS = BEST_EFFORT_RUNTIME_TARGETS
OFFICIAL_TARGETS_BY_TIER: dict[TierName, tuple[str, ...]] = {
    "tier1": TIER1_SUPPORTED_TARGETS,
    "tier2": TIER2_SUPPORTED_TARGETS,
}

assert SUPPORTED_TARGETS == OFFICIAL_TRANSPILATION_TARGETS_IN_TESTS == OFFICIAL_TARGETS
assert TIER1_SUPPORTED_TARGETS == TIER1_TARGETS
assert TIER2_SUPPORTED_TARGETS == TIER2_TARGETS
assert TIER1_SUPPORTED_TARGETS + TIER2_SUPPORTED_TARGETS == SUPPORTED_TARGETS
assert VERIFICATION_EXECUTABLE_TARGETS == ("python", "rust", "javascript", "cpp")
assert set(OFFICIAL_RUNTIME_TARGETS).isdisjoint(BEST_EFFORT_INTERNAL_RUNTIME_TARGETS)
assert set(OFFICIAL_RUNTIME_TARGETS) | set(TRANSPILATION_ONLY_TARGETS) == set(SUPPORTED_TARGETS)
assert set(BEST_EFFORT_INTERNAL_RUNTIME_TARGETS) <= set(TRANSPILATION_ONLY_TARGETS)
assert set(NO_RUNTIME_TARGETS) == {"wasm", "asm"}


def official_targets_for_tier(tier: TierName) -> tuple[str, ...]:
    """Devuelve el conjunto canónico de backends oficiales para ``tier``."""
    return OFFICIAL_TARGETS_BY_TIER[tier]


def matrix_targets_for_tier(
    tier: TierName,
    *,
    compatibility_matrix: dict[str, dict[str, str]] = BACKEND_COMPATIBILITY,
) -> tuple[str, ...]:
    """Devuelve los backends cuyo tier declarado en la matriz coincide con ``tier``."""
    return tuple(
        backend
        for backend in SUPPORTED_TARGETS
        if compatibility_matrix.get(backend, {}).get("tier") == tier
    )


def assert_tier_targets_match_policy(
    tier: TierName,
    *,
    compatibility_matrix: dict[str, dict[str, str]] = BACKEND_COMPATIBILITY,
    transpilers: Iterable[str] | None = None,
) -> tuple[str, ...]:
    """Valida que la matriz contractual y el contrato canónico publiquen el mismo tier."""
    expected = official_targets_for_tier(tier)
    declared = matrix_targets_for_tier(tier, compatibility_matrix=compatibility_matrix)
    assert declared == expected
    if transpilers is not None:
        assert set(declared).issubset(set(transpilers))
    return declared


def assert_official_targets_partition(
    *,
    compatibility_matrix: dict[str, dict[str, str]] = BACKEND_COMPATIBILITY,
    transpilers: Iterable[str] | None = None,
) -> dict[TierName, tuple[str, ...]]:
    """Valida que los 8 backends oficiales queden particionados exactamente por tiers."""
    partition = {
        tier: assert_tier_targets_match_policy(
            tier,
            compatibility_matrix=compatibility_matrix,
            transpilers=transpilers,
        )
        for tier in ("tier1", "tier2")
    }
    assert partition["tier1"] + partition["tier2"] == SUPPORTED_TARGETS
    return partition
