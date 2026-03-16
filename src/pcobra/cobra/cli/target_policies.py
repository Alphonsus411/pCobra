"""Políticas centralizadas de targets para comandos CLI."""

from __future__ import annotations

from argparse import ArgumentTypeError

from pcobra.cobra.transpilers.targets import OFFICIAL_TARGETS, normalize_target_name

# Fecha objetivo para retirar compatibilidad temporal de aliases legacy en CLI.
LEGACY_ALIAS_FLAG_RETIREMENT = "2026-06-30"
_ALLOW_LEGACY_TARGET_ALIASES = False

# Targets oficiales que además pueden ejecutarse en Docker.
DOCKER_EXECUTABLE_TARGETS = tuple(
    target for target in OFFICIAL_TARGETS if target in {"python", "javascript", "cpp", "rust"}
)

# Backend runtime que espera ``core.sandbox.ejecutar_en_contenedor``.
DOCKER_RUNTIME_BY_TARGET: dict[str, str] = {
    "python": "python",
    "javascript": "js",
    "cpp": "cpp",
    "rust": "rust",
}


def _official_targets_text() -> str:
    return ", ".join(OFFICIAL_TARGETS)


def set_legacy_target_aliases_enabled(enabled: bool) -> None:
    """Activa/desactiva compatibilidad temporal de aliases en parseo CLI."""
    global _ALLOW_LEGACY_TARGET_ALIASES
    _ALLOW_LEGACY_TARGET_ALIASES = bool(enabled)


def parse_target(value: str) -> str:
    """Valida target CLI; por defecto acepta solo nombres canónicos oficiales."""
    canonical = normalize_target_name(
        value,
        allow_legacy_aliases=_ALLOW_LEGACY_TARGET_ALIASES,
    )
    if canonical not in OFFICIAL_TARGETS:
        raise ArgumentTypeError(
            "Target no soportado: '{value}'. Usa uno canónico: {supported}.".format(
                value=value.strip(),
                supported=_official_targets_text(),
            )
        )
    return canonical


def parse_target_list(value: str) -> list[str]:
    """Valida una lista de targets separados por comas bajo la política activa."""
    parsed = [parse_target(item) for item in value.split(",") if item.strip()]
    if not parsed:
        raise ArgumentTypeError("La lista de targets no puede estar vacía")
    return parsed


def legacy_aliases_flag_help() -> str:
    """Texto de ayuda para la bandera de compatibilidad temporal."""
    return (
        "Permite aliases legacy de targets (temporal, retiro previsto: "
        f"{LEGACY_ALIAS_FLAG_RETIREMENT})."
    )


def resolve_docker_backend(target: str) -> str:
    """Resuelve backend runtime de Docker para un target oficial canónico."""
    normalized = parse_target(target)
    if normalized not in DOCKER_EXECUTABLE_TARGETS:
        supported = ", ".join(DOCKER_EXECUTABLE_TARGETS)
        raise ValueError(
            "El target '{target}' está soportado para transpilación, "
            "pero Docker solo ejecuta: {supported}.".format(
                target=normalized,
                supported=supported,
            )
        )
    return DOCKER_RUNTIME_BY_TARGET[normalized]
