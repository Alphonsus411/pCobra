"""Escritura de manifiestos del instalador Cobra."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Mapping, Sequence

from .project import BuildOptions, CobraProject
from .targets import BuildMode, TargetOS


@dataclass(frozen=True, slots=True)
class DependencyInfo:
    """Dependencia incluida o auditada durante el empaquetado."""

    name: str
    version: str | None = None
    source: str | None = None
    path: Path | str | None = None
    hashes: Mapping[str, str] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class BuildManifest:
    """Manifiesto reproducible de un build Cobra."""

    project: CobraProject
    executable_name: str
    target: str | TargetOS = "current"
    architecture: str = "native"
    mode: BuildMode | str = BuildMode.ONEDIR
    temp_dir: Path | str | None = None
    dist_dir: Path | str | None = None
    icon: Path | str | None = None
    hashes: Mapping[str, str] = field(default_factory=dict)
    cobra_version: str | None = None
    pyinstaller_version: str | None = None
    dependencies: Sequence[DependencyInfo] = field(default_factory=tuple)

    def to_dict(self) -> dict[str, object]:
        """Convierte el manifiesto a una estructura serializable como JSON."""

        project = self.project.normalized()
        return {
            "project_root": _stringify(project.project_root),
            "entrypoint": _stringify(project.entrypoint),
            "cobra_toml": _stringify(project.cobra_toml),
            "cobra_lock": _stringify(project.cobra_lock),
            "assets": [_stringify(path) for path in project.assets],
            "config": dict(project.config),
            "co_packages": [_stringify(path) for path in project.co_packages],
            "documentation": [_stringify(path) for path in project.documentation],
            "executable_name": self.executable_name,
            "target": _enum_value(self.target),
            "architecture": self.architecture,
            "mode": BuildMode.from_value(self.mode).value,
            "temp_dir": _stringify(self.temp_dir),
            "dist_dir": _stringify(self.dist_dir),
            "icon": _stringify(self.icon),
            "hashes": dict(self.hashes),
            "cobra_version": self.cobra_version,
            "pyinstaller_version": self.pyinstaller_version,
            "dependencies": [
                {
                    "name": dependency.name,
                    "version": dependency.version,
                    "source": dependency.source,
                    "path": _stringify(dependency.path),
                    "hashes": dict(dependency.hashes),
                }
                for dependency in self.dependencies
            ],
        }


def create_manifest(options: BuildOptions, entrypoint: Path, output_dir: Path, name: str) -> Path:
    """Crea un manifiesto JSON para el artefacto Cobra."""

    path = output_dir / "cobra-installer-manifest.json"
    manifest = BuildManifest(
        project=CobraProject(
            project_root=options.project_root,
            entrypoint=entrypoint,
            cobra_toml=Path(options.project_root) / "cobra.toml",
            cobra_lock=Path(options.project_root) / "cobra.lock",
            assets=options.assets,
            config=options.config,
        ),
        executable_name=name,
        target=options.target,
        architecture=options.architecture,
        mode=options.mode,
        temp_dir=options.temp_dir,
        dist_dir=output_dir,
        icon=options.icon,
    )
    payload = manifest.to_dict()
    payload["name"] = name
    payload["include_dependencies"] = options.include_dependencies
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return path


def _stringify(value: object) -> str | None:
    if value is None:
        return None
    return str(value)


def _enum_value(value: object) -> object:
    return value.value if hasattr(value, "value") else value


__all__ = ["BuildManifest", "DependencyInfo", "create_manifest"]
