"""Targets oficiales de transpilation por nivel de soporte."""

from typing import Final, Tuple

TIER1_TARGETS: Final[Tuple[str, ...]] = ("python", "rust", "javascript", "wasm")
TIER2_TARGETS: Final[Tuple[str, ...]] = ("go", "cpp", "java", "asm")
OFFICIAL_TARGETS: Final[Tuple[str, ...]] = TIER1_TARGETS + TIER2_TARGETS

TARGET_ALIASES: Final[dict[str, str]] = {
    "js": "javascript",
}

TARGET_FRIENDLY_LABELS: Final[dict[str, str]] = {
    "python": "Python",
    "rust": "Rust",
    "javascript": "JavaScript",
    "wasm": "WebAssembly",
    "go": "Go",
    "cpp": "C++",
    "java": "Java",
    "asm": "Ensamblador",
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


def target_cli_choices(available_targets: Tuple[str, ...] | list[str] | set[str]) -> tuple[str, ...]:
    """Devuelve targets canónicos oficiales preservando el orden oficial."""
    available = set(available_targets)
    return tuple(target for target in OFFICIAL_TARGETS if target in available)


def target_label(target: str) -> str:
    """Devuelve la etiqueta amigable de un target canónico."""
    canonical = normalize_target_name(target)
    return TARGET_FRIENDLY_LABELS.get(canonical, canonical)


def build_target_help_by_tier() -> str:
    """Devuelve ayuda agrupada por tier con etiqueta amigable + nombre canónico."""

    def _fmt(target: str) -> str:
        return f"{target_label(target)} ({target})"

    tier1 = ", ".join(_fmt(target) for target in TIER1_TARGETS)
    tier2 = ", ".join(_fmt(target) for target in TIER2_TARGETS)
    return f"Tier 1: {tier1}. Tier 2: {tier2}."
