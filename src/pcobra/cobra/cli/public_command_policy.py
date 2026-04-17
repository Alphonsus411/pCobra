"""Política de exposición de comandos CLI según perfil de visibilidad."""

from __future__ import annotations

from os import environ
from typing import Iterable

PUBLIC_COMMANDS: tuple[str, ...] = ("run", "build", "test", "mod")
INTERNAL_COMMANDS: tuple[str, ...] = (
    "legacy",
    "debug",
    "devops",
)
LEGACY_PUBLIC_COMMANDS: tuple[str, ...] = (
    "interactive",
    "compilar",
    "ejecutar",
    "modulos",
    "verificar",
    "docs",
    "plugins",
    "init",
    "crear",
    "paquete",
)
LEGACY_INTERNAL_COMMANDS: tuple[str, ...] = (
    "cache",
    "contenedor",
    "gui",
    "jupyter",
    "qualia",
    "agix",
)
LEGACY_OBSOLETE_COMMANDS: tuple[str, ...] = (
    "dependencias",
    "empaquetar",
    "bench",
    "benchmarks",
    "benchmarks2",
    "benchtranspilers",
    "benchthreads",
    "profile",
    "transpilar-inverso",
    "validar-sintaxis",
    "qa-validar",
)
COMMAND_VISIBILITY_MATRIX_MARKDOWN = """| Clase | Comandos |
|---|---|
| Públicos (UI v2) | run, build, test, mod |
| Internos (UI v2 / development) | legacy, debug, devops |
| Legacy públicos (UI v1) | interactive, compilar, ejecutar, modulos, verificar, docs, plugins, init, crear, paquete |
| Legacy internos (UI v1) | cache, contenedor, gui, jupyter, qualia, agix |
| Legacy obsoletos (UI v1) | dependencias, empaquetar, bench, benchmarks, benchmarks2, benchtranspilers, benchthreads, profile, transpilar-inverso, validar-sintaxis, qa-validar |
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


def filter_commands_for_profile(command_names: Iterable[str], profile: str) -> set[str]:
    """Devuelve el subconjunto de comandos visibles para `profile`."""

    normalized_profile = str(profile).strip().lower() or PROFILE_PUBLIC
    names = {name.strip().lower() for name in command_names}

    if normalized_profile == PROFILE_DEVELOPMENT:
        return names

    allowed = set(PUBLIC_COMMANDS)
    return names.intersection(allowed)


def filter_legacy_commands_for_profile(command_names: Iterable[str], profile: str) -> set[str]:
    """Filtra comandos de CLI legacy (v1) según perfil de exposición.

    Perfil `public`: conserva únicamente `LEGACY_PUBLIC_COMMANDS`.
    Perfil `development`: permite toda la superficie incluida la obsoleta para
    migración interna y pruebas de regresión.
    """

    normalized_profile = str(profile).strip().lower() or PROFILE_PUBLIC
    names = {name.strip().lower() for name in command_names}

    if normalized_profile == PROFILE_DEVELOPMENT:
        return names

    allowed = set(LEGACY_PUBLIC_COMMANDS)
    return names.intersection(allowed)


__all__ = [
    "PUBLIC_COMMANDS",
    "INTERNAL_COMMANDS",
    "LEGACY_PUBLIC_COMMANDS",
    "LEGACY_INTERNAL_COMMANDS",
    "LEGACY_OBSOLETE_COMMANDS",
    "COMMAND_VISIBILITY_MATRIX_MARKDOWN",
    "PROFILE_PUBLIC",
    "PROFILE_DEVELOPMENT",
    "COMMAND_PROFILES",
    "resolve_command_profile",
    "filter_commands_for_profile",
    "filter_legacy_commands_for_profile",
]
