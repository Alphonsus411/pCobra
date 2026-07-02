"""Tipos compartidos y detección de proyectos para el instalador Cobra."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Mapping, Sequence

try:  # pragma: no cover - Python < 3.11 compatibility path
    import tomllib
except ModuleNotFoundError:  # pragma: no cover
    tomllib = None  # type: ignore[assignment]

from .targets import BuildMode, Builder, BuilderConfig, TargetOS, normalize_target


class CobraInstallerError(RuntimeError):
    """Error base para fallos controlados durante el empaquetado Cobra."""


@dataclass(frozen=True, slots=True)
class ProjectResources:
    """Recursos relevantes encontrados dentro de una raíz de proyecto Cobra."""

    assets: Sequence[Path | str] = field(default_factory=tuple)
    config_dirs: Sequence[Path | str] = field(default_factory=tuple)
    co_packages: Sequence[Path | str] = field(default_factory=tuple)
    documentation: Sequence[Path | str] = field(default_factory=tuple)
    auxiliary_resources: Sequence[Path | str] = field(default_factory=tuple)

    def normalized(self, project_root: Path | str) -> "ProjectResources":
        """Devuelve una copia con rutas absolutas resueltas desde la raíz."""

        root = Path(project_root).expanduser().resolve()
        return ProjectResources(
            assets=tuple(_normalize_path(path, root) for path in self.assets),
            config_dirs=tuple(_normalize_path(path, root) for path in self.config_dirs),
            co_packages=tuple(_normalize_path(path, root) for path in self.co_packages),
            documentation=tuple(
                _normalize_path(path, root) for path in self.documentation
            ),
            auxiliary_resources=tuple(
                _normalize_path(path, root) for path in self.auxiliary_resources
            ),
        )


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
    config_dirs: Sequence[Path | str] = field(default_factory=tuple)
    auxiliary_resources: Sequence[Path | str] = field(default_factory=tuple)

    def normalized(self) -> "CobraProject":
        """Devuelve una copia con rutas absolutas resueltas desde la raíz."""

        root = Path(self.project_root).expanduser().resolve()
        return CobraProject(
            project_root=root,
            entrypoint=_normalize_optional_path(self.entrypoint, root),
            cobra_toml=_normalize_optional_path(
                self.cobra_toml or root / "cobra.toml", root
            ),
            cobra_lock=_normalize_optional_path(
                self.cobra_lock or root / "cobra.lock", root
            ),
            assets=tuple(_normalize_path(path, root) for path in self.assets),
            config=dict(self.config),
            co_packages=tuple(_normalize_path(path, root) for path in self.co_packages),
            documentation=tuple(
                _normalize_path(path, root) for path in self.documentation
            ),
            config_dirs=tuple(_normalize_path(path, root) for path in self.config_dirs),
            auxiliary_resources=tuple(
                _normalize_path(path, root) for path in self.auxiliary_resources
            ),
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
    builder: Builder | str = Builder.LOCAL
    builder_config: BuilderConfig | None = None
    mode: BuildMode | str = BuildMode.ONEDIR
    temp_dir: Path | str | None = None
    dist_dir: Path | str | None = None
    icon: Path | str | None = None
    assets: Sequence[Path | str] = field(default_factory=tuple)
    config: Mapping[str, object] = field(default_factory=dict)
    clean: bool = False
    include_dependencies: bool = True
    extra_args: Sequence[str] = field(default_factory=tuple)
    log_callback: Callable[[str], None] | None = None

    def normalized(self) -> "BuildOptions":
        """Devuelve una copia con rutas absolutas y valores derivados."""

        root = Path(self.project_root).expanduser().resolve()
        entrypoint = _normalize_optional_path(self.entrypoint, root)
        output_dir = _normalize_optional_path(
            self.output_dir or self.dist_dir or root / "dist", root
        )
        temp_dir = _normalize_optional_path(self.temp_dir or root / "build", root)
        return BuildOptions(
            project_root=root,
            entrypoint=entrypoint,
            output_dir=output_dir,
            name=self.name,
            target=normalize_target(self.target),
            architecture=self.architecture,
            builder=Builder.from_value(self.builder),
            builder_config=self.builder_config
            or BuilderConfig.from_value(self.builder),
            mode=BuildMode.from_value(self.mode),
            temp_dir=temp_dir,
            dist_dir=output_dir,
            icon=_normalize_optional_path(self.icon, root),
            assets=tuple(_normalize_path(path, root) for path in self.assets),
            config=dict(self.config),
            clean=self.clean,
            include_dependencies=self.include_dependencies,
            extra_args=tuple(self.extra_args),
            log_callback=self.log_callback,
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
    builder: Builder | str = Builder.LOCAL
    builder_config: BuilderConfig | None = None
    mode: BuildMode = BuildMode.ONEDIR
    executable_name: str | None = None
    temp_dir: Path | None = None
    dist_dir: Path | None = None
    hashes: Mapping[str, str] = field(default_factory=dict)
    cobra_version: str | None = None
    pyinstaller_version: str | None = None
    metadata: Mapping[str, object] = field(default_factory=dict)
    logs: tuple[str, ...] = ()


def discover_project(path: Path) -> CobraProject:
    """Detecta y normaliza un proyecto Cobra a partir de un archivo o directorio."""

    root = _discover_project_root(path)
    resources = collect_project_resources(root)
    entrypoint = find_entrypoint(root)
    config = _read_cobra_toml(root / "cobra.toml")
    return CobraProject(
        project_root=root,
        entrypoint=entrypoint,
        cobra_toml=root / "cobra.toml" if (root / "cobra.toml").is_file() else None,
        cobra_lock=root / "cobra.lock" if (root / "cobra.lock").is_file() else None,
        assets=resources.assets,
        config=config,
        co_packages=resources.co_packages,
        documentation=resources.documentation,
        config_dirs=resources.config_dirs,
        auxiliary_resources=resources.auxiliary_resources,
    ).normalized()


def find_entrypoint(project_root: Path) -> Path:
    """Resuelve el entrypoint del proyecto priorizando ``main.cobra``."""

    root = Path(project_root).expanduser().resolve()
    main_cobra = root / "main.cobra"
    if main_cobra.is_file():
        return main_cobra

    configured = _configured_entrypoints(root)
    if len(configured) == 1:
        return configured[0]
    if len(configured) > 1:
        formatted = ", ".join(str(path) for path in configured)
        raise CobraInstallerError(
            "No se pudo determinar un entrypoint único: cobra.toml contiene "
            f"varias rutas candidatas ({formatted}). Define solo una o crea main.cobra."
        )

    candidates = sorted(root.glob("*.cobra"))
    if len(candidates) == 1:
        return candidates[0]
    if len(candidates) > 1:
        formatted = ", ".join(path.name for path in candidates)
        raise CobraInstallerError(
            "No se pudo determinar el entrypoint Cobra: no existe main.cobra y hay "
            f"varios archivos .cobra en la raíz ({formatted}). Configura el entrypoint en cobra.toml."
        )

    raise CobraInstallerError(
        f"No se encontró entrypoint Cobra en {root}. Crea main.cobra o configura el entrypoint en cobra.toml."
    )


def collect_project_resources(project_root: Path) -> ProjectResources:
    """Recolecta recursos Cobra empaquetables bajo la raíz del proyecto."""

    root = Path(project_root).expanduser().resolve()
    if not root.is_dir():
        raise CobraInstallerError(
            f"La raíz del proyecto no existe o no es un directorio: {root}"
        )

    assets: list[Path] = []
    config_dirs: list[Path] = []
    co_packages: list[Path] = []
    documentation: list[Path] = []
    auxiliary: list[Path] = []

    for current_raw, dirs, files in os.walk(root):
        current = Path(current_raw)
        dirs[:] = [dirname for dirname in dirs if dirname not in _IGNORED_DIRS]
        if current.name == "assets":
            assets.append(current)
        if current.name == "config":
            config_dirs.append(current)
        for filename in files:
            path = current / filename
            suffix = path.suffix.lower()
            if suffix == ".co":
                co_packages.append(path)
            elif suffix in _DOCUMENTATION_SUFFIXES:
                documentation.append(path)
            elif path.name in _AUXILIARY_FILE_NAMES or suffix in _AUXILIARY_SUFFIXES:
                auxiliary.append(path)

    return ProjectResources(
        assets=tuple(sorted(assets)),
        config_dirs=tuple(sorted(config_dirs)),
        co_packages=tuple(sorted(co_packages)),
        documentation=tuple(sorted(documentation)),
        auxiliary_resources=tuple(sorted(auxiliary)),
    ).normalized(root)


def _discover_project_root(path: Path) -> Path:
    candidate = Path(path).expanduser().resolve()
    start = candidate.parent if candidate.is_file() else candidate
    if not start.exists():
        raise CobraInstallerError(f"La ruta del proyecto no existe: {candidate}")

    for current in (start, *start.parents):
        if (
            (current / "main.cobra").is_file()
            or (current / "cobra.toml").is_file()
            or (current / "cobra.lock").is_file()
        ):
            return current
    return start


def _configured_entrypoints(root: Path) -> list[Path]:
    config = _read_cobra_toml(root / "cobra.toml")
    raw_values = _find_entrypoint_values(config)
    resolved: list[Path] = []
    seen: set[Path] = set()
    for value in raw_values:
        path = _normalize_path(value, root)
        if path in seen:
            continue
        seen.add(path)
        if not path.is_file():
            raise CobraInstallerError(
                f"El entrypoint configurado en cobra.toml no existe: {path}"
            )
        resolved.append(path)
    return resolved


def _read_cobra_toml(path: Path) -> dict[str, object]:
    if not path.is_file():
        return {}
    if tomllib is None:
        raise CobraInstallerError(
            "No se puede leer cobra.toml: tomllib no está disponible en esta versión de Python."
        )
    try:
        return tomllib.loads(path.read_text(encoding="utf-8"))
    except tomllib.TOMLDecodeError as exc:  # type: ignore[union-attr]
        raise CobraInstallerError(f"cobra.toml no es válido: {exc}") from exc


def _find_entrypoint_values(config: Mapping[str, object]) -> list[str]:
    values: list[str] = []
    for key in ("entrypoint", "main", "source", "script"):
        value = config.get(key)
        if isinstance(value, str):
            values.append(value)
    for section_name in ("project", "package", "build", "app", "cobra"):
        section = config.get(section_name)
        if isinstance(section, Mapping):
            values.extend(_find_entrypoint_values(section))
    return values


def _normalize_optional_path(path: Path | str | None, root: Path) -> Path | None:
    if path is None:
        return None
    return _normalize_path(path, root)


def _normalize_path(path: Path | str, root: Path) -> Path:
    raw_path = Path(path).expanduser()
    if not raw_path.is_absolute():
        raw_path = root / raw_path
    return raw_path.resolve()


_IGNORED_DIRS = {
    ".git",
    ".hg",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".tox",
    ".venv",
    "__pycache__",
    "build",
    "dist",
    "node_modules",
    "venv",
}
_DOCUMENTATION_SUFFIXES = {".md", ".rst", ".txt"}
_AUXILIARY_SUFFIXES = {
    ".json",
    ".yaml",
    ".yml",
    ".ini",
    ".cfg",
    ".env",
    ".ico",
    ".png",
    ".jpg",
    ".jpeg",
    ".svg",
}
_AUXILIARY_FILE_NAMES = {
    "cobra.toml",
    "cobra.lock",
    "pyproject.toml",
    "requirements.txt",
    "LICENSE",
    "NOTICE",
}
