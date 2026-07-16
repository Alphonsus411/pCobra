"""Política de exposición de comandos CLI según perfil de visibilidad."""

from __future__ import annotations

from os import environ
from typing import Iterable

# `repl` es comando público oficial en UI v2; no debe tratarse como alias legacy.
PUBLIC_COMMANDS_CONTRACT: tuple[str, ...] = (
    "run", "build", "test", "mod", "repl", "gui"
)
PUBLIC_COMMANDS: tuple[str, ...] = PUBLIC_COMMANDS_CONTRACT
PUBLIC_V2_HIDDEN_COMPAT_COMMANDS: tuple[str, ...] = ("paquete", "hub")
if PUBLIC_COMMANDS != PUBLIC_COMMANDS_CONTRACT:
    raise RuntimeError(
        "Contrato público inválido: PUBLIC_COMMANDS debe mantenerse en "
        "('run', 'build', 'test', 'mod', 'repl', 'gui')."
    )
INTERNAL_COMMANDS: tuple[str, ...] = (
    "legacy",
    "debug",
    "devops",
)


COMMAND_VISIBILITY_MATRIX_MARKDOWN = """| Clase | Comandos |
|---|---|
| Públicos (UI v2) | run, build, test, mod, repl, gui |
| Desarrollo (visibles solo con perfil `development`) | installer, paquete, hub |
| Internos (UI v2 / development) | legacy, debug, devops |
| Legacy públicos (UI v1) | *(ninguno; reservado a `development`)* |
| Legacy internos (UI v1) | *(ninguno)* |
| Legacy obsoletos (UI v1) | *(ninguno)* |
|"""

PROFILE_PUBLIC = "public"
PROFILE_DEVELOPMENT = "development"
COMMAND_PROFILES: tuple[str, ...] = (PROFILE_PUBLIC, PROFILE_DEVELOPMENT)


def resolve_command_profile(default: str = PROFILE_PUBLIC) -> str:
    """Resuelve el perfil de exposición desde entorno.

    Prioridad:
    1) COBRA_CLI_COMMAND_PROFILE con valores explícitos (public/development).
    2) COBRA_DEV_MODE=1 fuerza `development` para sesiones internas.
    3) `default` como fallback seguro.
    """

    profile = (environ.get("COBRA_CLI_COMMAND_PROFILE") or "").strip().lower()
    if profile in COMMAND_PROFILES:
        return profile

    if (environ.get("COBRA_DEV_MODE") or "").strip() == "1":
        return PROFILE_DEVELOPMENT

    return default


def _normalize_command_names(command_names: Iterable[str]) -> set[str]:
    return {name.strip().lower() for name in command_names}


def is_public_v2_visible_command(name: str) -> bool:
    """Indica si `name` pertenece al contrato público visible de CLI v2."""

    return name.strip().lower() in PUBLIC_COMMANDS


def is_public_v2_hidden_compat_command(name: str) -> bool:
    """Indica si `name` es compatibilidad pública v2 registrada pero oculta."""

    return name.strip().lower() in PUBLIC_V2_HIDDEN_COMPAT_COMMANDS


def visible_commands_for_profile(
    command_names: Iterable[str], profile: str
) -> set[str]:
    """Devuelve comandos visibles para `profile`.

    - `public`: solo la intersección entre `command_names` y `PUBLIC_COMMANDS`.
    - `development`: todos los comandos disponibles recibidos en `command_names`.
    """

    normalized_profile = str(profile).strip().lower() or PROFILE_PUBLIC
    names = _normalize_command_names(command_names)

    if normalized_profile == PROFILE_DEVELOPMENT:
        return names

    return {name for name in names if is_public_v2_visible_command(name)}


def registered_commands_for_profile(
    command_names: Iterable[str], profile: str
) -> set[str]:
    """Devuelve comandos que deben registrarse como subparsers para `profile`.

    En perfil público v2, `paquete` y `hub` son compatibilidad runtime: se
    registran para poder ejecutarse, pero no forman parte de la capa visible.
    """

    normalized_profile = str(profile).strip().lower() or PROFILE_PUBLIC
    names = _normalize_command_names(command_names)

    if normalized_profile == PROFILE_DEVELOPMENT:
        return names

    return {
        name
        for name in names
        if is_public_v2_visible_command(name)
        or is_public_v2_hidden_compat_command(name)
    }


def filter_commands_for_profile(command_names: Iterable[str], profile: str) -> set[str]:
    """Compatibilidad: alias de la capa visible de comandos v2."""

    return visible_commands_for_profile(command_names, profile)


def filter_legacy_commands_for_profile(
    command_names: Iterable[str], profile: str
) -> set[str]:
    """Devuelve comandos legacy visibles según perfil.

    La superficie v1/legacy queda reservada para sesiones de desarrollo y
    migración; el perfil público no debe exponer esos comandos.
    """

    normalized_profile = str(profile).strip().lower() or PROFILE_PUBLIC
    names = {name.strip().lower() for name in command_names}

    if normalized_profile == PROFILE_DEVELOPMENT:
        return names

    return set()


__all__ = [
    "PUBLIC_COMMANDS_CONTRACT",
    "PUBLIC_COMMANDS",
    "PUBLIC_V2_HIDDEN_COMPAT_COMMANDS",
    "INTERNAL_COMMANDS",
    "COMMAND_VISIBILITY_MATRIX_MARKDOWN",
    "PROFILE_PUBLIC",
    "PROFILE_DEVELOPMENT",
    "COMMAND_PROFILES",
    "resolve_command_profile",
    "is_public_v2_visible_command",
    "is_public_v2_hidden_compat_command",
    "visible_commands_for_profile",
    "registered_commands_for_profile",
    "filter_commands_for_profile",
    "filter_legacy_commands_for_profile",
]
