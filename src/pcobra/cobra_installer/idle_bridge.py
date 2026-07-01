"""Puente delgado para que el IDLE delegue el empaquetado.

No debe contener lógica de construcción: el IDLE y este módulo solo llaman a
``package_current_project``.
"""

from __future__ import annotations

from pathlib import Path

from .project import BuildResult
from .runtime_builder import package_current_project


def package_from_idle(project_root: str | Path, **kwargs: object) -> BuildResult:
    """Delegación explícita desde el IDLE hacia la API pública del instalador."""

    return package_current_project(project_root, **kwargs)
