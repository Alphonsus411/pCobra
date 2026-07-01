"""Tipos compartidos para el instalador Cobra."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Mapping, Sequence

from .targets import BuildMode, TargetOS


class CobraInstallerError(RuntimeError):
    """Error base para fallos controlados durante el empaquetado Cobra."""


@dataclass(frozen=True, slots=True)
class CobraProject:
    """Descripción normalizada de los recursos detectados en un proyecto Cobra."""

    project_root: Path | str = Path.cwd()
    entrypoint: Path | str | None = None
    cobra_toml: Path | str | None = None
    cobra_lock: Path | str | None = None
    assets: Sequence[Path | str] = field(default_factory=tuple)
    config: Mapping[str, object] = field(default_factory=dict)
    co_packages: Sequence[Path | str] = field(default_factory=tuple)
    documentation: Sequence[Path | str] = field(default_factory=tuple)

    def normalized(self) -> "CobraProject":
        """Devuelve una copia con rutas absolutas resueltas desde la raíz."""

        root = Path(self.project_root).expanduser().resolve()
        return CobraProject(
            project_root=root,
            entrypoint=_normalize_optional_path(self.entrypoint, root),
            cobra_toml=_normalize_optional_path(self.cobra_toml or root / "cobra.toml", root),
            cobra_lock=_normalize_optional_path(self.cobra_lock or root / "cobra.lock", root),
            assets=tuple(_normalize_path(path, root) for path in self.assets),
            config=dict(self.config),
            co_packages=tuple(_normalize_path(path, root) for path in self.co_packages),
            documentation=tuple(_normalize_path(path, root) for path in self.documentation),
        )


@dataclass(frozen=True, slots=True)
class BuildOptions:
    """Opciones para construir un artefacto instalable de un proyecto Cobra."""

    project_root: Path | str = Path.cwd()
    entrypoint: Path | str | None = None
    output_dir: Path | str | None = None
    name: str | None = None
    target: str | TargetOS = "current"
    architecture: str = "native"
    mode: BuildMode | str = BuildMode.ONEDIR
    temp_dir: Path | str | None = None
    dist_dir: Path | str | None = None
    icon: Path | str | None = None
    assets: Sequence[Path | str] = field(default_factory=tuple)
    config: Mapping[str, object] = field(default_factory=dict)
    clean: bool = False
    include_dependencies: bool = True
    extra_args: Sequence[str] = field(default_factory=tuple)

    def normalized(self) -> "BuildOptions":
        """Devuelve una copia con rutas absolutas y valores derivados."""

        root = Path(self.project_root).expanduser().resolve()
        entrypoint = _normalize_optional_path(self.entrypoint, root)
        output_dir = _normalize_optional_path(self.output_dir or self.dist_dir or root / "dist", root)
        temp_dir = _normalize_optional_path(self.temp_dir or root / "build", root)
        return BuildOptions(
            project_root=root,
            entrypoint=entrypoint,
            output_dir=output_dir,
            name=self.name,
            target=self.target,
            architecture=self.architecture,
            mode=BuildMode.from_value(self.mode),
            temp_dir=temp_dir,
            dist_dir=output_dir,
            icon=_normalize_optional_path(self.icon, root),
            assets=tuple(_normalize_path(path, root) for path in self.assets),
            config=dict(self.config),
            clean=self.clean,
            include_dependencies=self.include_dependencies,
            extra_args=tuple(self.extra_args),
        )


@dataclass(frozen=True, slots=True)
class BuildResult:
    """Resultado estable de un proceso de construcción."""

    success: bool
    artifact_path: Path | None = None
    project_root: Path | None = None
    output_dir: Path | None = None
    target: str | TargetOS = "current"
    architecture: str = "native"
    mode: BuildMode = BuildMode.ONEDIR
    executable_name: str | None = None
    temp_dir: Path | None = None
    dist_dir: Path | None = None
    hashes: Mapping[str, str] = field(default_factory=dict)
    cobra_version: str | None = None
    pyinstaller_version: str | None = None
    metadata: Mapping[str, object] = field(default_factory=dict)
    logs: tuple[str, ...] = ()


def _normalize_optional_path(path: Path | str | None, root: Path) -> Path | None:
    if path is None:
        return None
    return _normalize_path(path, root)


def _normalize_path(path: Path | str, root: Path) -> Path:
    raw_path = Path(path).expanduser()
    if not raw_path.is_absolute():
        raw_path = root / raw_path
    return raw_path.resolve()
