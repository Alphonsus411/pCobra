"""Políticas centralizadas de targets para comandos CLI."""

from __future__ import annotations

from argparse import ArgumentTypeError

from pcobra.cobra.transpilers.targets import (
    OFFICIAL_TARGETS,
    build_target_help_by_tier,
    normalize_target_name,
    require_official_target_subset,
    target_cli_choices,
)

# Todos los destinos oficiales de generación/transpilación.
OFFICIAL_TRANSPILATION_TARGETS = tuple(OFFICIAL_TARGETS)

# Targets oficiales con tooling oficial de ejecución en contenedor/sandbox Docker.
OFFICIAL_RUNTIME_TARGETS = target_cli_choices(("python", "javascript", "cpp", "rust"))

# Targets oficiales que hoy son solo de generación y no prometen runtime oficial.
TRANSPILATION_ONLY_TARGETS = tuple(
    target for target in OFFICIAL_TRANSPILATION_TARGETS if target not in OFFICIAL_RUNTIME_TARGETS
)

# Targets best-effort conservados fuera del contrato oficial de runtime.
BEST_EFFORT_RUNTIME_TARGETS = target_cli_choices(("go", "java"))

# Targets sin runtime automatizado en la CLI/suite actual.
NO_RUNTIME_TARGETS = tuple(
    target for target in TRANSPILATION_ONLY_TARGETS if target not in BEST_EFFORT_RUNTIME_TARGETS
)

# Alias semántico conservado para la UX existente.
DOCKER_EXECUTABLE_TARGETS = OFFICIAL_RUNTIME_TARGETS

# Backend runtime que espera ``core.sandbox.ejecutar_en_contenedor``.
DOCKER_RUNTIME_BY_TARGET: dict[str, str] = {target: target for target in OFFICIAL_RUNTIME_TARGETS}

# Targets con verificación ejecutable oficial dentro de la CLI actual.
VERIFICATION_EXECUTABLE_TARGETS = target_cli_choices(("python", "javascript"))

require_official_target_subset(
    OFFICIAL_RUNTIME_TARGETS,
    context="pcobra.cobra.cli.target_policies.OFFICIAL_RUNTIME_TARGETS",
)
require_official_target_subset(
    VERIFICATION_EXECUTABLE_TARGETS,
    context="pcobra.cobra.cli.target_policies.VERIFICATION_EXECUTABLE_TARGETS",
)
require_official_target_subset(
    BEST_EFFORT_RUNTIME_TARGETS,
    context="pcobra.cobra.cli.target_policies.BEST_EFFORT_RUNTIME_TARGETS",
)
require_official_target_subset(
    NO_RUNTIME_TARGETS,
    context="pcobra.cobra.cli.target_policies.NO_RUNTIME_TARGETS",
)


OFFICIAL_TRANSPILATION_TARGETS_HELP = build_target_help_by_tier(OFFICIAL_TRANSPILATION_TARGETS)
OFFICIAL_RUNTIME_TARGETS_HELP = build_target_help_by_tier(OFFICIAL_RUNTIME_TARGETS)
VERIFICATION_EXECUTABLE_TARGETS_HELP = build_target_help_by_tier(VERIFICATION_EXECUTABLE_TARGETS)


def official_transpilation_targets_text() -> str:
    return ", ".join(OFFICIAL_TRANSPILATION_TARGETS)


def official_runtime_targets_text() -> str:
    return ", ".join(OFFICIAL_RUNTIME_TARGETS)


def verification_runtime_targets_text() -> str:
    return ", ".join(VERIFICATION_EXECUTABLE_TARGETS)


def transpilation_only_targets_text() -> str:
    return ", ".join(TRANSPILATION_ONLY_TARGETS)


def build_runtime_capability_message(*, capability: str, allowed_targets: tuple[str, ...]) -> str:
    return (
        "Targets oficiales de transpilación: {official}. "
        "Solo tienen runtime oficial para {capability}: {allowed}. "
        "Los targets {non_runtime} siguen siendo salidas oficiales de generación de código, "
        "pero no equivalen a un runtime oficial ni a soporte oficial de librerías en ejecución. "
        "Targets solo transpilación: {transpilation_only}."
    ).format(
        official=official_transpilation_targets_text(),
        capability=capability,
        allowed=", ".join(allowed_targets),
        non_runtime=", ".join(TRANSPILATION_ONLY_TARGETS),
        transpilation_only=transpilation_only_targets_text(),
    )


def invalid_target_error(value: str) -> str:
    return "Target no soportado: '{value}'. Usa uno canónico oficial: {supported}.".format(
        value=value.strip(),
        supported=official_transpilation_targets_text(),
    )


def restricted_target_error(*, unsupported: list[str], capability: str, allowed_targets: tuple[str, ...]) -> str:
    return (
        "Los targets {unsupported} son oficiales para transpilación, "
        "pero no tienen runtime oficial para {capability}. "
        "Generar código para esos targets no implica paridad de ejecución real "
        "ni soporte oficial de librerías equivalente a `python`, `rust`, `javascript` o `cpp`. "
        "Targets oficiales: {official}. Usa solo: {allowed}. "
        "Targets solo transpilación: {transpilation_only}."
    ).format(
        unsupported=", ".join(unsupported),
        capability=capability,
        official=official_transpilation_targets_text(),
        allowed=", ".join(allowed_targets),
        transpilation_only=transpilation_only_targets_text(),
    )


def parse_target(value: str) -> str:
    """Valida target CLI aceptando solo nombres canónicos oficiales."""
    canonical = normalize_target_name(value)
    if canonical not in OFFICIAL_TRANSPILATION_TARGETS:
        raise ArgumentTypeError(invalid_target_error(value))
    return canonical


def parse_runtime_target(value: str, *, allowed_targets: tuple[str, ...], capability: str) -> str:
    """Valida un target oficial restringido a una capacidad con runtime."""
    canonical = parse_target(value)
    if canonical not in allowed_targets:
        raise ArgumentTypeError(
            restricted_target_error(
                unsupported=[canonical],
                capability=capability,
                allowed_targets=allowed_targets,
            )
        )
    return canonical


def parse_target_list(value: str) -> list[str]:
    """Valida una lista de targets separados por comas."""
    parsed = [parse_target(item) for item in value.split(",") if item.strip()]
    if not parsed:
        raise ArgumentTypeError("La lista de targets no puede estar vacía")
    return parsed


def parse_restricted_target_list(value: str, allowed_targets: tuple[str, ...], capability: str) -> list[str]:
    """Valida una lista de targets oficiales restringida a una capacidad concreta."""
    parsed = parse_target_list(value)
    unsupported = [target for target in parsed if target not in allowed_targets]
    if unsupported:
        raise ArgumentTypeError(
            restricted_target_error(
                unsupported=unsupported,
                capability=capability,
                allowed_targets=allowed_targets,
            )
        )
    return parsed


def resolve_docker_backend(target: str) -> str:
    """Resuelve backend runtime de Docker para un target oficial canónico.

    Algunos targets oficiales (`go`, `java`, `wasm`, `asm`) son de transpilación
    oficial, pero no exponen runtime Docker oficial.
    """
    try:
        normalized = parse_runtime_target(
            target,
            allowed_targets=DOCKER_EXECUTABLE_TARGETS,
            capability="ejecución en contenedor Docker",
        )
    except ArgumentTypeError as exc:
        raise ValueError(str(exc)) from exc
    return DOCKER_RUNTIME_BY_TARGET[normalized]
