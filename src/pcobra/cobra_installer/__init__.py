"""API pública para construir instaladores de proyectos Cobra.

El paquete concentra la lógica de empaquetado fuera del IDLE. Las interfaces
visuales deben limitarse a invocar :func:`package_current_project` o a usar el
puente delgado de :mod:`pcobra.cobra_installer.idle_bridge`.
"""

from __future__ import annotations

from .manifest import BuildManifest, DependencyInfo
from .project import (
    BuildOptions,
    BuildResult,
    CobraInstallerError,
    CobraProject,
    ProjectResources,
    collect_project_resources,
    discover_project,
    find_entrypoint,
)
from .targets import BuildMode, TargetOS
from .transpile import TranspileResult, transpile_project
from .validator import ValidationErrorDetail, ValidationResult, validate_project
from .runtime_builder import (
    RuntimePreparationResult,
    build_project,
    package_current_project,
    prepare_runtime,
)

__all__ = [
    "BuildManifest",
    "BuildMode",
    "BuildOptions",
    "BuildResult",
    "CobraProject",
    "CobraInstallerError",
    "ProjectResources",
    "collect_project_resources",
    "discover_project",
    "find_entrypoint",
    "DependencyInfo",
    "TargetOS",
    "TranspileResult",
    "transpile_project",
    "ValidationErrorDetail",
    "ValidationResult",
    "RuntimePreparationResult",
    "build_project",
    "validate_project",
    "package_current_project",
    "prepare_runtime",
]
