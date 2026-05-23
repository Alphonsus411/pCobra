"""Targets oficiales de transpilation por nivel de soporte."""

from __future__ import annotations

from typing import Final

from pcobra.cobra.architecture.backend_policy import PUBLIC_BACKENDS
from pcobra.cobra.config.transpile_targets import (
    OFFICIAL_TARGETS,
    TARGETS_BY_TIER,
    TIER1_TARGETS,
    TIER2_TARGETS,
)

EXPECTED_CANONICAL_TARGETS: Final[tuple[str, ...]] = PUBLIC_BACKENDS


def _canonical_diff_report(
    *,
    current: tuple[str, ...],
    expected: tuple[str, ...] = EXPECTED_CANONICAL_TARGETS,
) -> str:
    missing = tuple(target for target in expected if target not in current)
    extras = tuple(target for target in current if target not in expected)
    return f"missing={missing or '∅'}; extras={extras or '∅'}; current={current}; expected={expected}"


if tuple(TARGETS_BY_TIER) != ("tier_1", "tier_2"):
    raise RuntimeError(
        "TARGETS_BY_TIER debe exponer exactamente los grupos tier_1 y tier_2. "
        f"current={tuple(TARGETS_BY_TIER)}"
    )

if OFFICIAL_TARGETS != EXPECTED_CANONICAL_TARGETS:
    raise RuntimeError(
        "OFFICIAL_TARGETS debe mantener exactamente los nombres públicos canónicos en orden. "
        + _canonical_diff_report(current=OFFICIAL_TARGETS)
    )
