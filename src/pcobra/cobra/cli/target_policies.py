"""Políticas centralizadas de targets para comandos CLI."""

from __future__ import annotations

from argparse import ArgumentTypeError

from pcobra.cobra.transpilers.targets import OFFICIAL_TARGETS, normalize_target_name

# Todos los destinos oficiales de generación/transpilación.
OFFICIAL_TRANSPILATION_TARGETS = OFFICIAL_TARGETS

# Targets oficiales con tooling oficial de ejecución en contenedor/sandbox Docker.
OFFICIAL_RUNTIME_TARGETS = ("python", "javascript", "cpp", "rust")

# Targets oficiales que hoy son solo de generación y no prometen runtime oficial.
TRANSPILATION_ONLY_TARGETS = tuple(
    target for target in OFFICIAL_TRANSPILATION_TARGETS if target not in OFFICIAL_RUNTIME_TARGETS
)

# Alias semántico conservado para la UX existente.
DOCKER_EXECUTABLE_TARGETS = OFFICIAL_RUNTIME_TARGETS

# Backend runtime que espera ``core.sandbox.ejecutar_en_contenedor``.
DOCKER_RUNTIME_BY_TARGET: dict[str, str] = {target: target for target in OFFICIAL_RUNTIME_TARGETS}

# Targets con verificación ejecutable oficial dentro de la CLI actual.
VERIFICATION_EXECUTABLE_TARGETS = ("python", "javascript")


def _official_targets_text() -> str:
    return ", ".join(OFFICIAL_TRANSPILATION_TARGETS)


def parse_target(value: str) -> str:
    """Valida target CLI aceptando solo nombres canónicos oficiales."""
    canonical = normalize_target_name(value)
    if canonical not in OFFICIAL_TRANSPILATION_TARGETS:
        raise ArgumentTypeError(
            "Target no soportado: '{value}'. Usa uno canónico: {supported}.".format(
                value=value.strip(),
                supported=_official_targets_text(),
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
            "Los targets {unsupported} son oficiales para transpilación, pero no "
            "están disponibles para {capability}. Usa solo: {allowed}.".format(
                unsupported=", ".join(unsupported),
                capability=capability,
                allowed=", ".join(allowed_targets),
            )
        )
    return parsed


def resolve_docker_backend(target: str) -> str:
    """Resuelve backend runtime de Docker para un target oficial canónico.

    Algunos targets oficiales (`go`, `java`, `wasm`, `asm`) son de transpilación
    oficial, pero no exponen runtime Docker oficial.
    """
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
