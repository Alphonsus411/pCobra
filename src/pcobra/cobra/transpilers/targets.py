"""Targets oficiales de transpilation por nivel de soporte."""

from __future__ import annotations

from typing import Final

EXPECTED_CANONICAL_TARGETS: Final[tuple[str, ...]] = (
    "python",
    "rust",
    "javascript",
    "wasm",
    "go",
    "cpp",
    "java",
    "asm",
)

_TIER1_SIZE: Final[int] = 4
TIER1_TARGETS: Final[tuple[str, ...]] = EXPECTED_CANONICAL_TARGETS[:_TIER1_SIZE]
TIER2_TARGETS: Final[tuple[str, ...]] = EXPECTED_CANONICAL_TARGETS[_TIER1_SIZE:]
OFFICIAL_TARGETS: Final[tuple[str, ...]] = EXPECTED_CANONICAL_TARGETS


def _canonical_diff_report(
    *,
    current: tuple[str, ...],
    expected: tuple[str, ...] = EXPECTED_CANONICAL_TARGETS,
) -> str:
    missing = tuple(target for target in expected if target not in current)
    extras = tuple(target for target in current if target not in expected)
    return f"missing={missing or '∅'}; extras={extras or '∅'}; current={current}; expected={expected}"


if TIER1_TARGETS != EXPECTED_CANONICAL_TARGETS[:_TIER1_SIZE] or TIER2_TARGETS != EXPECTED_CANONICAL_TARGETS[_TIER1_SIZE:]:
    raise RuntimeError(
        "TIER1_TARGETS/TIER2_TARGETS deben permanecer fijados al contrato canónico de 8 targets. "
        + _canonical_diff_report(current=TIER1_TARGETS + TIER2_TARGETS)
    )

if OFFICIAL_TARGETS != EXPECTED_CANONICAL_TARGETS:
    raise RuntimeError(
        "OFFICIAL_TARGETS debe mantener exactamente los 8 nombres canónicos en orden. "
        + _canonical_diff_report(current=OFFICIAL_TARGETS)
    )
