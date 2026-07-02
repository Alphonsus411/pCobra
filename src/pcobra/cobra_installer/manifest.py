"""Escritura de manifiestos del instalador Cobra."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from datetime import UTC, datetime
from importlib import metadata
from pathlib import Path
from typing import Mapping, Sequence

from .project import BuildOptions, CobraProject
from .targets import BuildMode, Builder, TargetOS

BUILD_MANIFEST_NAME = "cobra_build_manifest.json"
LEGACY_MANIFEST_NAME = "cobra-installer-manifest.json"


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
    version: str | None = None
    backend: str | None = None
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
    cobrahub_dependencies: Sequence[DependencyInfo] = field(default_factory=tuple)
    generated_at: datetime | str | None = None
    build_duration_seconds: float | int | None = None
    runtime_included: bool = False
    included_assets: Sequence[Path | str] = field(default_factory=tuple)
    final_size_bytes: int | None = None
    executable_path: Path | str | None = None

    def to_dict(self) -> dict[str, object]:
        """Convierte el manifiesto a una estructura serializable como JSON.

        La forma de salida es estable: listas y mapas se ordenan y el JSON que
        escribe :func:`write_manifest_json` usa claves ordenadas. Los campos
        variables (fecha y duración) se pueden inyectar en tests mediante
        ``generated_at`` y ``build_duration_seconds`` para no depender del reloj.
        """

        project = self.project.normalized()
        dependencies = _dependencies_to_list(self.dependencies)
        cobrahub_dependencies = _dependencies_to_list(self.cobrahub_dependencies)
        assets = _sorted_strings(project.assets)
        included_assets = _sorted_strings(self.included_assets or project.assets)
        return {
            "project": _project_name(project, self.executable_name),
            "version": self.version or _project_version(project),
            "backend": self.backend,
            "target": _enum_value(self.target),
            "architecture": self.architecture,
            "build_mode": BuildMode.from_value(self.mode).value,
            "mode": BuildMode.from_value(self.mode).value,
            "cobra_version": self.cobra_version,
            "pyinstaller_version": self.pyinstaller_version,
            "cobrahub_dependencies": cobrahub_dependencies,
            "dependencies": dependencies,
            "hashes": _sorted_mapping(self.hashes),
            "generated_at": _isoformat(self.generated_at),
            "build_duration_seconds": self.build_duration_seconds,
            "runtime_included": self.runtime_included,
            "assets_included": included_assets,
            "final_size_bytes": self.final_size_bytes,
            "executable_path": _stringify(self.executable_path),
            "project_root": _stringify(project.project_root),
            "entrypoint": _stringify(project.entrypoint),
            "cobra_toml": _stringify(project.cobra_toml),
            "cobra_lock": _stringify(project.cobra_lock),
            "assets": assets,
            "config": _stable_json_value(dict(project.config)),
            "co_packages": _sorted_strings(project.co_packages),
            "documentation": _sorted_strings(project.documentation),
            "config_dirs": _sorted_strings(project.config_dirs),
            "auxiliary_resources": _sorted_strings(project.auxiliary_resources),
            "executable_name": self.executable_name,
            "temp_dir": _stringify(self.temp_dir),
            "dist_dir": _stringify(self.dist_dir),
            "icon": _stringify(self.icon),
        }


def create_manifest(
    options: BuildOptions, entrypoint: Path, output_dir: Path, name: str
) -> Path:
    """Crea el manifiesto JSON estable para el artefacto Cobra.

    El archivo principal se genera en ``dist/cobra_build_manifest.json``. También
    se escribe ``cobra-installer-manifest.json`` con el mismo contenido para no
    romper integraciones que aún consuman el nombre anterior.
    """

    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / BUILD_MANIFEST_NAME
    executable_path = _default_executable_path(output_dir, name, options)
    project = CobraProject(
        project_root=options.project_root,
        entrypoint=entrypoint,
        cobra_toml=Path(options.project_root) / "cobra.toml",
        cobra_lock=Path(options.project_root) / "cobra.lock",
        assets=options.assets,
        config=options.config,
    )
    hashes = _build_hashes(project.normalized(), executable_path)
    manifest = BuildManifest(
        project=project,
        executable_name=name,
        version=_project_version(project),
        backend=_backend(options),
        target=options.target,
        architecture=options.architecture,
        mode=options.mode,
        temp_dir=options.temp_dir,
        dist_dir=output_dir,
        icon=options.icon,
        hashes=hashes,
        cobra_version=_installed_version("pcobra"),
        pyinstaller_version=_installed_version("pyinstaller"),
        generated_at=datetime.now(UTC),
        build_duration_seconds=0.0,
        runtime_included=Path(options.temp_dir or Path(options.project_root) / "build")
        .joinpath("runtime")
        .exists(),
        included_assets=options.assets,
        final_size_bytes=_path_size(executable_path),
        executable_path=executable_path,
    )
    payload = manifest.to_dict()
    payload["name"] = name
    payload["include_dependencies"] = options.include_dependencies
    write_manifest_json(path, payload)
    write_manifest_json(output_dir / LEGACY_MANIFEST_NAME, payload)
    return path


def write_manifest_json(path: Path, payload: Mapping[str, object]) -> None:
    """Escribe JSON con serialización estable para comparaciones en tests."""

    path.write_text(
        json.dumps(
            _stable_json_value(payload), ensure_ascii=False, indent=2, sort_keys=True
        )
        + "\n",
        encoding="utf-8",
    )


def _build_hashes(project: CobraProject, executable_path: Path) -> dict[str, str]:
    hashes: dict[str, str] = {}
    for path in _existing_files(
        project.entrypoint,
        project.cobra_toml,
        project.cobra_lock,
        *project.assets,
        executable_path,
    ):
        hashes[str(path)] = f"sha256:{_sha256_path(path)}"
    return hashes


def _existing_files(*paths: Path | str | None) -> tuple[Path, ...]:
    return tuple(
        Path(path) for path in paths if path is not None and Path(path).is_file()
    )


def _sha256_path(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _default_executable_path(
    output_dir: Path, name: str, options: BuildOptions
) -> Path:
    suffix = ".exe" if _enum_value(options.target) == TargetOS.WINDOWS.value else ""
    executable = f"{name}{suffix}"
    if BuildMode.from_value(options.mode) is BuildMode.ONEDIR:
        return output_dir / name / executable
    return output_dir / executable


def _path_size(path: Path) -> int | None:
    if path.is_file():
        return path.stat().st_size
    if path.is_dir():
        return sum(child.stat().st_size for child in path.rglob("*") if child.is_file())
    return None


def _backend(options: BuildOptions) -> str:
    configured = _nested_config_value(
        options.config, "build", "backend"
    ) or _nested_config_value(options.config, "project", "backend")
    if configured is not None:
        return str(configured)
    return Builder.from_value(options.builder).value


def _project_name(project: CobraProject, fallback: str) -> str:
    return str(
        _nested_config_value(project.config, "project", "name")
        or _nested_config_value(project.config, "package", "name")
        or fallback
    )


def _project_version(project: CobraProject) -> str | None:
    value = _nested_config_value(
        project.config, "project", "version"
    ) or _nested_config_value(project.config, "package", "version")
    return str(value) if value is not None else None


def _nested_config_value(
    config: Mapping[str, object], section: str, key: str
) -> object | None:
    candidate = config.get(section)
    if isinstance(candidate, Mapping):
        return candidate.get(key)
    return None


def _installed_version(distribution: str) -> str | None:
    try:
        return metadata.version(distribution)
    except metadata.PackageNotFoundError:
        return None


def _dependencies_to_list(
    dependencies: Sequence[DependencyInfo],
) -> list[dict[str, object]]:
    return sorted(
        (
            {
                "name": dependency.name,
                "version": dependency.version,
                "source": dependency.source,
                "path": _stringify(dependency.path),
                "hashes": _sorted_mapping(dependency.hashes),
            }
            for dependency in dependencies
        ),
        key=lambda item: (str(item["name"]), str(item["version"]), str(item["path"])),
    )


def _sorted_mapping(mapping: Mapping[str, str]) -> dict[str, str]:
    return {str(key): str(mapping[key]) for key in sorted(mapping)}


def _sorted_strings(paths: Sequence[Path | str]) -> list[str]:
    return sorted(str(path) for path in paths)


def _stable_json_value(value: object) -> object:
    if isinstance(value, Mapping):
        return {str(key): _stable_json_value(value[key]) for key in sorted(value)}
    if isinstance(value, (list, tuple)):
        return [_stable_json_value(item) for item in value]
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, datetime):
        return _isoformat(value)
    return value


def _isoformat(value: datetime | str | None) -> str:
    if value is None:
        value = datetime.now(UTC)
    if isinstance(value, str):
        return value
    if value.tzinfo is None:
        value = value.replace(tzinfo=UTC)
    return value.astimezone(UTC).isoformat().replace("+00:00", "Z")


def _stringify(value: object) -> str | None:
    if value is None:
        return None
    return str(value)


def _enum_value(value: object) -> object:
    return value.value if hasattr(value, "value") else value


__all__ = [
    "BUILD_MANIFEST_NAME",
    "LEGACY_MANIFEST_NAME",
    "BuildManifest",
    "DependencyInfo",
    "create_manifest",
    "write_manifest_json",
]
