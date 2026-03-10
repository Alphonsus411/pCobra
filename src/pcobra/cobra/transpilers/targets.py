"""Targets oficiales de transpilation por nivel de soporte."""

from typing import Final, Tuple

TIER1_TARGETS: Final[Tuple[str, ...]] = ("python", "rust", "js", "wasm")
TIER2_TARGETS: Final[Tuple[str, ...]] = ("go", "cpp", "java", "asm")
OFFICIAL_TARGETS: Final[Tuple[str, ...]] = TIER1_TARGETS + TIER2_TARGETS

