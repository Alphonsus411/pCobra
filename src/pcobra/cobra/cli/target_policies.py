"""Políticas centralizadas de targets para comandos CLI."""

from __future__ import annotations

from argparse import ArgumentTypeError

from pcobra.cobra.transpilers.targets import OFFICIAL_TARGETS, normalize_target_name

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


def parse_target(value: str) -> str:
    """Normaliza aliases legacy de targets para argumentos CLI."""
    return normalize_target_name(value)


def parse_target_list(value: str) -> list[str]:
    """Normaliza una lista de targets separada por comas."""
    parsed = [parse_target(item) for item in value.split(",") if item.strip()]
    if not parsed:
        raise ArgumentTypeError("La lista de targets no puede estar vacía")
    return parsed


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

