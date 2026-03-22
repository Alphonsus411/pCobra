"""Targets oficiales de transpilation por nivel de soporte."""

from __future__ import annotations

from typing import Final, Iterable, Literal, Tuple

MarkupKind = Literal["plain", "markdown", "rst"]

TIER1_TARGETS: Final[Tuple[str, ...]] = ("python", "rust", "javascript", "wasm")
TIER2_TARGETS: Final[Tuple[str, ...]] = ("go", "cpp", "java", "asm")
OFFICIAL_TARGETS: Final[Tuple[str, ...]] = TIER1_TARGETS + TIER2_TARGETS

TARGET_FRIENDLY_LABELS: Final[dict[str, str]] = {
    "python": "Python",
    "rust": "Rust",
    "javascript": "JavaScript",
    "wasm": "WebAssembly",
    "go": "Go",
    "cpp": "cpp",
    "java": "Java",
    "asm": "asm",
}


def normalize_target_name(target: str) -> str:
    """Normaliza *target* al nombre canónico usado internamente."""
    return target.strip().lower()


def resolution_candidates(target: str) -> Tuple[str, ...]:
    """Devuelve posibles nombres válidos para resolver configuraciones canónicas."""
    canonical = normalize_target_name(target)
    return (canonical,)


def target_cli_choices(available_targets: Tuple[str, ...] | list[str] | set[str]) -> tuple[str, ...]:
    """Devuelve targets canónicos oficiales preservando el orden oficial."""
    available = set(available_targets)
    return tuple(target for target in OFFICIAL_TARGETS if target in available)


def require_official_target_subset(
    available_targets: Iterable[str],
    *,
    context: str,
) -> tuple[str, ...]:
    """Valida que todos los targets pertenezcan al conjunto oficial."""
    normalized = tuple(normalize_target_name(target) for target in available_targets)
    extras = sorted(set(normalized) - set(OFFICIAL_TARGETS))
    if extras:
        raise RuntimeError(
            "Targets fuera del conjunto canónico en {context}: {extras}. "
            "Permitidos: {allowed}".format(
                context=context,
                extras=", ".join(extras),
                allowed=", ".join(OFFICIAL_TARGETS),
            )
        )
    return normalized


def require_exact_official_targets(
    available_targets: Iterable[str],
    *,
    context: str,
) -> tuple[str, ...]:
    """Valida que un conjunto coincida exactamente con ``OFFICIAL_TARGETS``."""
    normalized = require_official_target_subset(available_targets, context=context)
    ordered = target_cli_choices(normalized)
    missing = [target for target in OFFICIAL_TARGETS if target not in normalized]
    if missing or len(set(normalized)) != len(OFFICIAL_TARGETS):
        details = []
        if missing:
            details.append(f"faltan: {', '.join(missing)}")
        extra_duplicates = [
            target for target in OFFICIAL_TARGETS if normalized.count(target) > 1
        ]
        if extra_duplicates:
            details.append(f"duplicados: {', '.join(sorted(set(extra_duplicates)))}")
        raise RuntimeError(
            "Conjunto de targets desalineado con OFFICIAL_TARGETS en {context} ({details})".format(
                context=context,
                details="; ".join(details) or "orden/cantidad inválidos",
            )
        )
    return ordered


def require_exact_tier_targets(
    available_targets: Iterable[str],
    *,
    expected_tier: tuple[str, ...],
    context: str,
) -> tuple[str, ...]:
    """Valida que un conjunto coincida exactamente con un tier oficial."""
    normalized = require_official_target_subset(available_targets, context=context)
    ordered = target_cli_choices(normalized)
    expected_order = tuple(target for target in OFFICIAL_TARGETS if target in expected_tier)
    missing = [target for target in expected_order if target not in normalized]
    extras = sorted(set(normalized) - set(expected_order))
    if missing or extras or len(set(normalized)) != len(expected_order):
        details = []
        if missing:
            details.append(f"faltan: {', '.join(missing)}")
        if extras:
            details.append(f"sobran: {', '.join(extras)}")
        duplicated = [target for target in expected_order if normalized.count(target) > 1]
        if duplicated:
            details.append(f"duplicados: {', '.join(sorted(set(duplicated)))}")
        raise RuntimeError(
            "Conjunto de targets desalineado con {context} ({details})".format(
                context=context,
                details="; ".join(details) or "orden/cantidad inválidos",
            )
        )
    return tuple(target for target in ordered if target in expected_order)


def target_label(target: str) -> str:
    """Devuelve la etiqueta amigable de un target canónico."""
    canonical = normalize_target_name(target)
    return TARGET_FRIENDLY_LABELS.get(canonical, canonical)


def target_tier(target: str) -> str:
    """Devuelve el tier público de un target canónico."""
    canonical = normalize_target_name(target)
    if canonical in TIER1_TARGETS:
        return "Tier 1"
    if canonical in TIER2_TARGETS:
        return "Tier 2"
    raise RuntimeError(f"Target fuera de política: {target}")


def format_target_name(target: str, *, markup: MarkupKind = "plain") -> str:
    """Formatea un target canónico para documentación/CLI."""
    canonical = normalize_target_name(target)
    if markup in {"markdown", "rst"}:
        return f"``{canonical}``" if markup == "rst" else f"`{canonical}`"
    return canonical


def format_target_sequence(
    targets: Iterable[str],
    *,
    markup: MarkupKind = "plain",
    separator: str = ", ",
) -> str:
    """Formatea una secuencia ordenada de targets canónicos."""
    normalized = target_cli_choices(require_official_target_subset(targets, context="format_target_sequence"))
    return separator.join(format_target_name(target, markup=markup) for target in normalized)


def official_target_rows(
    targets: Iterable[str] | None = None,
) -> tuple[dict[str, str], ...]:
    """Devuelve filas documentales derivadas de la política canónica."""
    chosen = OFFICIAL_TARGETS if targets is None else target_cli_choices(
        require_official_target_subset(targets, context="official_target_rows")
    )
    return tuple(
        {
            "target": target,
            "label": target_label(target),
            "tier": target_tier(target),
        }
        for target in chosen
    )


def build_target_help_by_tier(
    available_targets: Iterable[str] | None = None,
) -> str:
    """Devuelve ayuda agrupada por tier con etiqueta amigable + nombre canónico."""

    def _fmt(target: str) -> str:
        label = target_label(target)
        return target if label == target else f"{label} ({target})"

    choices = (
        target_cli_choices(OFFICIAL_TARGETS)
        if available_targets is None
        else target_cli_choices(require_official_target_subset(available_targets, context="build_target_help_by_tier"))
    )
    tier1_choices = tuple(target for target in TIER1_TARGETS if target in choices)
    tier2_choices = tuple(target for target in TIER2_TARGETS if target in choices)
    sections = []
    if tier1_choices:
        sections.append("Tier 1: " + ", ".join(_fmt(target) for target in tier1_choices) + ".")
    if tier2_choices:
        sections.append("Tier 2: " + ", ".join(_fmt(target) for target in tier2_choices) + ".")
    return " ".join(sections)


def build_tier_summary_lines(*, markup: MarkupKind = "plain") -> tuple[str, ...]:
    """Devuelve líneas resumidas de tiers derivadas de la fuente canónica."""
    return (
        f"**Tier 1**: {format_target_sequence(TIER1_TARGETS, markup=markup)}.",
        f"**Tier 2**: {format_target_sequence(TIER2_TARGETS, markup=markup)}.",
    )
