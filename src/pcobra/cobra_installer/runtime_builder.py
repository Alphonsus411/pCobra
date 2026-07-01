"""Orquestación principal de construcción fuera del IDLE."""

from __future__ import annotations

from dataclasses import replace
from pathlib import Path

from .manifest import create_manifest
from .project import BuildOptions, BuildResult, CobraInstallerError
from .spec_writer import write_spec
from .validator import discover_entrypoint, validate_build_options


def build_project(options: BuildOptions | None = None, **overrides: object) -> BuildResult:
    """Construye un proyecto Cobra usando una API programática estable.

    La implementación inicial prepara directorios, manifiesto y especificación
    mínima para que PyInstaller/CLI puedan integrarse sin acoplar lógica al IDLE.
    """

    base = options or BuildOptions()
    if overrides:
        base = replace(base, **overrides)
    normalized = validate_build_options(base)
    entrypoint = normalized.entrypoint or discover_entrypoint(Path(normalized.project_root))
    if entrypoint is None:
        raise CobraInstallerError(
            f"No se encontró un punto de entrada Cobra en {normalized.project_root}"
        )

    output_dir = Path(normalized.output_dir or Path(normalized.project_root) / "dist")
    output_dir.mkdir(parents=True, exist_ok=True)
    name = normalized.name or entrypoint.stem
    manifest_path = create_manifest(normalized, entrypoint, output_dir, name)
    spec_path = write_spec(normalized, entrypoint, output_dir, name)
    return BuildResult(
        success=True,
        artifact_path=spec_path,
        project_root=Path(normalized.project_root),
        output_dir=output_dir,
        target=normalized.target,
        architecture=normalized.architecture,
        mode=normalized.mode,
        executable_name=name,
        temp_dir=Path(normalized.temp_dir) if normalized.temp_dir is not None else None,
        dist_dir=output_dir,
        metadata={"entrypoint": str(entrypoint), "manifest": str(manifest_path), "name": name},
        logs=("Proyecto preparado para empaquetado.",),
    )


def package_current_project(project_root: str | Path | None = None, **kwargs: object) -> BuildResult:
    """Empaqueta el proyecto actual; punto único que debe llamar el IDLE."""

    options = BuildOptions(project_root=project_root or Path.cwd(), **kwargs)
    return build_project(options)
