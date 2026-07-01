"""Validación de proyectos para el instalador Cobra."""

from __future__ import annotations

from pathlib import Path

from .project import BuildOptions, CobraInstallerError

COBRA_EXTENSIONS = (".cobra", ".co")


def validate_project(options: BuildOptions) -> BuildOptions:
    """Valida opciones y devuelve una versión normalizada."""

    normalized = options.normalized()
    root = Path(normalized.project_root)
    if not root.exists() or not root.is_dir():
        raise CobraInstallerError(f"El proyecto no existe o no es una carpeta: {root}")
    if normalized.entrypoint is not None and not normalized.entrypoint.exists():
        raise CobraInstallerError(f"El punto de entrada no existe: {normalized.entrypoint}")
    return normalized


def discover_entrypoint(project_root: Path) -> Path | None:
    """Busca un punto de entrada Cobra común dentro del proyecto."""

    for name in ("main.cobra", "main.co", "app.cobra", "app.co"):
        candidate = project_root / name
        if candidate.exists() and candidate.is_file():
            return candidate
    for extension in COBRA_EXTENSIONS:
        matches = sorted(project_root.glob(f"*{extension}"))
        if matches:
            return matches[0]
    return None
