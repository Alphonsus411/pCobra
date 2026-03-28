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

TIER1_TARGETS: Final[tuple[str, ...]] = ("python", "rust", "javascript", "wasm")
TIER2_TARGETS: Final[tuple[str, ...]] = ("go", "cpp", "java", "asm")
OFFICIAL_TARGETS: Final[tuple[str, ...]] = TIER1_TARGETS + TIER2_TARGETS

if TIER1_TARGETS != EXPECTED_CANONICAL_TARGETS[:4] or TIER2_TARGETS != EXPECTED_CANONICAL_TARGETS[4:]:
    raise RuntimeError(
        "TIER1_TARGETS/TIER2_TARGETS deben permanecer fijados al contrato canónico de 8 targets"
    )

if OFFICIAL_TARGETS != EXPECTED_CANONICAL_TARGETS:
    raise RuntimeError(
        "OFFICIAL_TARGETS debe mantener exactamente los 8 nombres canónicos en orden"
    )
