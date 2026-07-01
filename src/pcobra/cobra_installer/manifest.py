"""Escritura de manifiestos del instalador Cobra."""

from __future__ import annotations

import json
from pathlib import Path

from .project import BuildOptions


def create_manifest(options: BuildOptions, entrypoint: Path, output_dir: Path, name: str) -> Path:
    """Crea un manifiesto JSON mínimo para el artefacto."""

    path = output_dir / "cobra-installer-manifest.json"
    payload = {
        "name": name,
        "project_root": str(options.project_root),
        "entrypoint": str(entrypoint),
        "target": options.target,
        "include_dependencies": options.include_dependencies,
    }
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return path
