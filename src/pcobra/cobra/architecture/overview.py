"""Resumen arquitectónico oficial de frontera pública e internas.

Este módulo define el contrato de alto nivel para evitar deriva entre:
- documentación,
- validaciones de arranque de CLI,
- y rutas de ejecución build/runtime.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Final


PUBLIC_LANGUAGE_BOUNDARY: Final[str] = "cobra"
PUBLIC_CLI_V2_COMMANDS: Final[tuple[str, ...]] = ("run", "build", "test", "mod")

# Toda ruta de usuario termina resolviendo backend mediante esta fachada.
USER_ROUTE_BACKEND_ENTRYPOINT: Final[str] = "pcobra.cobra.build.backend_pipeline"
OFFICIAL_FLOW: Final[tuple[str, ...]] = (
    "Frontend Cobra",
    "BackendPipeline",
    "Bindings",
)

# Superficies no públicas: mantener solo para transición interna controlada.
INTERNAL_MIGRATION_ONLY_SURFACES: Final[dict[str, tuple[str, ...] | str]] = {
    "cli_v1": "internal migration only",
    "legacy_targets": "internal migration only",
    "obsolete_commands": (
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
    ),
}


@dataclass(frozen=True, slots=True)
class PublicArchitectureOverview:
    """Snapshot corto del contrato público efectivo."""

    language: str
    cli_commands_v2: tuple[str, ...]
    user_backend_entrypoint: str
    internal_migration_only: dict[str, tuple[str, ...] | str]


PUBLIC_ARCHITECTURE_OVERVIEW: Final[PublicArchitectureOverview] = (
    PublicArchitectureOverview(
        language=PUBLIC_LANGUAGE_BOUNDARY,
        cli_commands_v2=PUBLIC_CLI_V2_COMMANDS,
        user_backend_entrypoint=USER_ROUTE_BACKEND_ENTRYPOINT,
        internal_migration_only=INTERNAL_MIGRATION_ONLY_SURFACES,
    )
)

# Diagrama de flujo corto (sin cambios en AST).
PUBLIC_FLOW_DIAGRAM: Final[str] = (
    "Frontend Cobra -> BackendPipeline -> Bindings"
)


def validate_public_architecture_overview() -> None:
    """Garantiza una frontera pública única y estable."""
    if PUBLIC_LANGUAGE_BOUNDARY != "cobra":
        raise RuntimeError("La frontera pública de lenguaje debe ser únicamente 'cobra'.")

    if PUBLIC_CLI_V2_COMMANDS != ("run", "build", "test", "mod"):
        raise RuntimeError(
            "La CLI pública v2 debe exponer exactamente run/build/test/mod."
        )

    if USER_ROUTE_BACKEND_ENTRYPOINT != "pcobra.cobra.build.backend_pipeline":
        raise RuntimeError(
            "Toda ruta de usuario debe pasar por pcobra.cobra.build.backend_pipeline."
        )
    if OFFICIAL_FLOW != ("Frontend Cobra", "BackendPipeline", "Bindings"):
        raise RuntimeError(
            "El flujo oficial debe permanecer fijo: Frontend Cobra -> BackendPipeline -> Bindings."
        )


validate_public_architecture_overview()


__all__ = [
    "PUBLIC_LANGUAGE_BOUNDARY",
    "PUBLIC_CLI_V2_COMMANDS",
    "USER_ROUTE_BACKEND_ENTRYPOINT",
    "OFFICIAL_FLOW",
    "INTERNAL_MIGRATION_ONLY_SURFACES",
    "PublicArchitectureOverview",
    "PUBLIC_ARCHITECTURE_OVERVIEW",
    "PUBLIC_FLOW_DIAGRAM",
    "validate_public_architecture_overview",
]
