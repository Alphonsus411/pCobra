"""Generación de especificaciones de empaquetado."""

from __future__ import annotations

from pathlib import Path

from .project import BuildOptions


def write_spec(options: BuildOptions, entrypoint: Path, output_dir: Path, name: str) -> Path:
    """Escribe una especificación inicial legible por humanos."""

    path = output_dir / f"{name}.cobra-installer.toml"
    path.write_text(
        "\n".join(
            [
                f'name = "{name}"',
                f'project_root = "{Path(options.project_root)}"',
                f'entrypoint = "{entrypoint}"',
                f'target = "{options.target}"',
                f'include_dependencies = {str(options.include_dependencies).lower()}',
                "",
            ]
        ),
        encoding="utf-8",
    )
    return path
