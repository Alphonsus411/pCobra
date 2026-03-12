"""Targets oficiales de transpilation por nivel de soporte."""

from typing import Final, Tuple

TIER1_TARGETS: Final[Tuple[str, ...]] = ("python", "rust", "javascript", "wasm")
TIER2_TARGETS: Final[Tuple[str, ...]] = ("go", "cpp", "java", "asm")
OFFICIAL_TARGETS: Final[Tuple[str, ...]] = TIER1_TARGETS + TIER2_TARGETS

TARGET_ALIASES: Final[dict[str, str]] = {
    "js": "javascript",
}


def normalize_target_name(target: str) -> str:
    """Normaliza *target* al nombre canónico usado internamente."""
    normalized = target.strip().lower()
    return TARGET_ALIASES.get(normalized, normalized)




def resolution_candidates(target: str) -> Tuple[str, ...]:
    """Devuelve posibles nombres válidos para resolver compatibilidad retroactiva."""
    canonical = normalize_target_name(target)
    aliases = tuple(alias for alias, canon in TARGET_ALIASES.items() if canon == canonical)
    return (canonical, *aliases)

def build_target_help_by_tier() -> str:
    """Devuelve una cadena de ayuda agrupada por tier usando nombres canónicos."""
    tier1 = ", ".join(TIER1_TARGETS)
    tier2 = ", ".join(TIER2_TARGETS)
    return f"Tier 1: {tier1}. Tier 2: {tier2}."
