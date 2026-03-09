"""Constantes compartidas de targets soportados para la suite de tests."""

TIER1_TARGETS = ("python", "rust", "js", "wasm")
TIER2_TARGETS = ("go", "cpp", "java", "asm")
SUPPORTED_TARGETS = TIER1_TARGETS + TIER2_TARGETS
RUNNABLE_TARGETS = ("python", "js", "go", "cpp", "rust", "java")
