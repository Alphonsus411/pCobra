"""Targets oficiales de transpilation por nivel de soporte."""

from __future__ import annotations

from typing import Final

TIER1_TARGETS: Final[tuple[str, ...]] = ("python", "rust", "javascript", "wasm")
TIER2_TARGETS: Final[tuple[str, ...]] = ("go", "cpp", "java", "asm")
OFFICIAL_TARGETS: Final[tuple[str, ...]] = TIER1_TARGETS + TIER2_TARGETS
