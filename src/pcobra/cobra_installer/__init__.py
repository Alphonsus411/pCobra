"""API pública para construir instaladores de proyectos Cobra.

El paquete concentra la lógica de empaquetado fuera del IDLE. Las interfaces
visuales deben limitarse a invocar :func:`package_current_project` o a usar el
puente delgado de :mod:`pcobra.cobra_installer.idle_bridge`.
"""

from __future__ import annotations

from .project import BuildOptions, BuildResult, CobraInstallerError
from .runtime_builder import build_project, package_current_project

__all__ = [
    "BuildOptions",
    "BuildResult",
    "CobraInstallerError",
    "build_project",
    "package_current_project",
]
