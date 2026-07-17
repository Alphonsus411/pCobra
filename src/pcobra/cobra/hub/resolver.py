"""Resolución de dependencias Cobra para proyectos instalables.

Este módulo lee ``cobra.toml`` y ``cobra.lock``, detecta imports Cobra usados por
el proyecto y coordina la localización/descarga de paquetes vía CobraHub sin
reinventar el formato ``.co`` ni la caché existente bajo ``pcobra.cobra``.
"""

from __future__ import annotations

import json
import re
import tomllib
from pathlib import Path
from typing import Any, Mapping, Sequence

from pcobra.cobra.packaging import normalizar_nombre_paquete, validar_version_paquete
from pcobra.cobra.hub.installation import CobraHubResolver
from pcobra.cobra.hub.integrity import normalize_sha256
from pcobra.cobra.hub.models import (
    CobraHubResolution, DeclaredDependency, DependencyResolutionResult, LockedDependency,
)
from pcobra.cobra_installer.project import CobraInstallerError

__all__ = [
    "CobraDependencyError",
    "DeclaredDependency",
    "LockedDependency",
    "DependencyResolutionResult",
    "detect_cobra_imports",
    "read_declared_dependencies",
    "read_lockfile",
    "resolve_project_dependencies",
    "write_lockfile",
]


class CobraDependencyError(CobraInstallerError):
    """Error controlado de dependencias apto para CLI e IDLE."""





_IMPORT_RE = re.compile(
    r"^\s*(?:usar\s+(?P<usar>\"[^\"]+\"|'[^']+'|[A-Za-z_][\w]*(?:\.[A-Za-z_][\w]*)+)|import\s+(?P<import>\"[^\"]+\"|'[^']+'))",
    re.MULTILINE,
)
_SHA256_RE = re.compile(r"^[0-9a-fA-F]{64}$")
_LOCK_VERSION = 1
_IGNORED_DIRS = {
    ".git",
    ".hg",
    ".svn",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
}


def resolve_project_dependencies(
    project_root: str | Path,
    *,
    resolver: CobraHubResolver | None = None,
    fail_on_unused_declared: bool = False,
) -> DependencyResolutionResult:
    """Resuelve y valida las dependencias Cobra de ``project_root``.

    Valida que los imports usados estén declarados, que las versiones declaradas
    coincidan con el lockfile cuando existe, que no haya conflictos transitivos y
    que los hashes de los artefactos coincidan con ``cobra.lock``. Si no existe
    lockfile, lo genera con las descargas/localizaciones resueltas.
    """

    root = Path(project_root).resolve()
    declared = read_declared_dependencies(root / "cobra.toml")
    used_imports = detect_cobra_imports(root)
    missing = tuple(sorted(used_imports - set(declared)))
    if missing:
        raise CobraDependencyError(
            "Dependencias Cobra no declaradas en cobra.toml: " + ", ".join(missing)
        )

    if fail_on_unused_declared:
        unused = tuple(sorted(set(declared) - used_imports))
        if unused:
            raise CobraDependencyError(
                "Dependencias Cobra declaradas pero no usadas: " + ", ".join(unused)
            )

    lock_path = root / "cobra.lock"
    locked = read_lockfile(lock_path) if lock_path.exists() else {}
    _validate_declared_against_lock(declared, locked)

    hub = resolver or CobraHubResolver()
    resolved: dict[str, CobraHubResolution] = {}
    requested_versions = {name: dep.version for name, dep in declared.items()}
    dependency_chains = {
        name: f"proyecto -> {name}=={dep.version}"
        for name, dep in declared.items()
    }
    pending = sorted(requested_versions.items())

    while pending:
        name, version = pending.pop(0)
        if name in resolved:
            continue
        lock_entry = locked.get(name)
        resolution = hub.resolve(
            name,
            version,
            expected_sha256=lock_entry.sha256 if lock_entry else None,
            source=lock_entry.source if lock_entry else None,
        )
        if resolution.version != version:
            raise CobraDependencyError(
                f"Conflicto de versión para {name}: se pidió {version}, "
                f"pero CobraHub resolvió {resolution.version}. "
                f"Cadena: {dependency_chains[name]}."
            )
        resolved[name] = resolution

        for transitive_name, transitive_version in sorted(
            resolution.dependencies.items()
        ):
            chain = (
                f"{dependency_chains[name]} -> "
                f"{transitive_name}=={transitive_version}"
            )
            requested = requested_versions.get(transitive_name)
            if requested is not None and requested != transitive_version:
                previous_chain = dependency_chains[transitive_name]
                raise CobraDependencyError(
                    f"Conflicto de versiones para {transitive_name}: "
                    f"se requieren versiones incompatibles {requested} y {transitive_version}. "
                    f"Cadena existente: {previous_chain}. "
                    f"Cadena nueva: {chain}."
                )
            if requested is None:
                requested_versions[transitive_name] = transitive_version
                dependency_chains[transitive_name] = chain
                pending.append((transitive_name, transitive_version))

    created = False
    if not lock_path.exists():
        write_lockfile(lock_path, resolved)
        created = True

    return DependencyResolutionResult(
        declared=declared,
        used_imports=used_imports,
        resolved=resolved,
        lockfile_path=lock_path,
        lockfile_created=created,
        missing_declarations=missing,
        dependency_chains=dependency_chains,
        metadata={"schema_version": 2, "resolver": "cobrahub"},
    )


def read_declared_dependencies(path: str | Path) -> dict[str, DeclaredDependency]:
    """Lee dependencias Cobra declaradas en ``cobra.toml``.

    Formatos soportados:
    - ``[dependencies] paquete = "1.2.3"``
    - ``[cobra.dependencies] paquete = "1.2.3"``
    - ``[project] dependencies = ["paquete==1.2.3"]``
    """

    toml_path = Path(path)
    if not toml_path.exists():
        return {}
    try:
        data = tomllib.loads(toml_path.read_text(encoding="utf-8"))
    except (OSError, tomllib.TOMLDecodeError) as exc:
        raise CobraDependencyError(f"No se pudo leer cobra.toml: {exc}") from exc

    raw: dict[str, Any] = {}
    for key_path in (("dependencies",), ("cobra", "dependencies")):
        section = _get_mapping(data, key_path)
        if section:
            raw.update(section)
    project_deps = _get_mapping(data, ("project",)).get("dependencies")
    if isinstance(project_deps, list):
        raw.update(_parse_dependency_list(project_deps))

    declared: dict[str, DeclaredDependency] = {}
    for raw_name, raw_version in raw.items():
        name = _normalize_dependency_name(str(raw_name))
        version = _normalize_version_spec(raw_version, name)
        if name in declared and declared[name].version != version:
            raise CobraDependencyError(
                f"Conflicto de versiones declaradas para {name}: {declared[name].version} y {version}."
            )
        declared[name] = DeclaredDependency(name=name, version=version)
    return declared


def read_lockfile(path: str | Path) -> dict[str, LockedDependency]:
    """Lee versiones y hashes desde ``cobra.lock`` JSON o TOML."""

    lock_path = Path(path)
    try:
        text = lock_path.read_text(encoding="utf-8")
    except OSError as exc:
        raise CobraDependencyError(f"No se pudo leer cobra.lock: {exc}") from exc
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        try:
            data = tomllib.loads(text)
        except tomllib.TOMLDecodeError as exc:
            raise CobraDependencyError(
                f"cobra.lock no es JSON ni TOML válido: {exc}"
            ) from exc

    packages = data.get("packages") if isinstance(data, Mapping) else None
    entries: Sequence[Any]
    if isinstance(packages, list):
        entries = packages
    elif isinstance(packages, Mapping):
        entries = [
            (
                {"name": name, **value}
                if isinstance(value, Mapping)
                else {"name": name, "version": value}
            )
            for name, value in packages.items()
        ]
    elif isinstance(data, list):
        entries = data
    else:
        entries = []

    locked: dict[str, LockedDependency] = {}
    for entry in entries:
        if (
            not isinstance(entry, Mapping)
            or "name" not in entry
            or "version" not in entry
        ):
            raise CobraDependencyError(
                "cobra.lock contiene una entrada de paquete inválida."
            )
        name = _normalize_dependency_name(str(entry["name"]))
        version = validar_version_paquete(str(entry["version"]))
        sha256 = entry.get("sha256") or entry.get("checksum") or entry.get("hash")
        if isinstance(sha256, str):
            sha256 = normalize_sha256(sha256)
            if not _SHA256_RE.fullmatch(sha256):
                raise CobraDependencyError(
                    f"Hash SHA-256 inválido en cobra.lock para {name}."
                )
        else:
            sha256 = None
        source = entry.get("source")
        locked[name] = LockedDependency(
            name=name,
            version=version,
            sha256=sha256,
            source=str(source) if source else None,
        )
    return locked


def write_lockfile(
    path: str | Path, resolved: Mapping[str, CobraHubResolution]
) -> None:
    """Genera ``cobra.lock`` estable cuando no existe."""

    lock_path = Path(path)
    payload = {
        "version": _LOCK_VERSION,
        "packages": [
            {
                "name": item.name,
                "version": item.version,
                "sha256": item.sha256,
                "source": item.source,
            }
            for item in sorted(resolved.values(), key=lambda value: value.name)
        ],
    }
    lock_path.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def detect_cobra_imports(project_root: str | Path) -> set[str]:
    """Detecta estáticamente imports Cobra usados por archivos ``.cobra``/``.co``."""

    root = Path(project_root)
    imports: set[str] = set()
    for file in _iter_cobra_sources(root):
        try:
            text = file.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for match in _IMPORT_RE.finditer(text):
            raw = match.group("usar") or match.group("import") or ""
            module = raw.strip().strip("\"'")
            if _is_local_import(module):
                continue
            package = module.split(".", 1)[0]
            imports.add(_normalize_dependency_name(package))
    return imports


def _iter_cobra_sources(root: Path):
    for path in root.rglob("*"):
        if any(part in _IGNORED_DIRS for part in path.relative_to(root).parts):
            continue
        if path.is_file() and path.suffix in {".cobra", ".co"}:
            yield path


def _is_local_import(module: str) -> bool:
    return (
        module.startswith((".", "/"))
        or module.endswith((".cobra", ".co"))
        or "/" in module
        or "\\" in module
    )


def _normalize_dependency_name(name: str) -> str:
    try:
        return normalizar_nombre_paquete(name)
    except ValueError as exc:
        raise CobraDependencyError(
            f"Nombre de dependencia Cobra inválido: {name}"
        ) from exc


def _normalize_version_spec(value: Any, name: str) -> str:
    if isinstance(value, Mapping):
        value = value.get("version")
    if not isinstance(value, str):
        raise CobraDependencyError(
            f"Versión inválida para {name}: debe ser una cadena SemVer exacta."
        )
    version = value.strip()
    if version.startswith("=="):
        version = version[2:].strip()
    try:
        return validar_version_paquete(version)
    except ValueError as exc:
        raise CobraDependencyError(
            f"Versión inválida para {name}: use SemVer exacto MAJOR.MINOR.PATCH."
        ) from exc


def _parse_dependency_list(values: Sequence[Any]) -> dict[str, str]:
    parsed: dict[str, str] = {}
    for value in values:
        if not isinstance(value, str) or "==" not in value:
            continue
        name, version = value.split("==", 1)
        parsed[name.strip()] = version.strip()
    return parsed


def _get_mapping(data: Mapping[str, Any], key_path: Sequence[str]) -> Mapping[str, Any]:
    current: Any = data
    for key in key_path:
        if not isinstance(current, Mapping):
            return {}
        current = current.get(key, {})
    return current if isinstance(current, Mapping) else {}


def _validate_declared_against_lock(
    declared: Mapping[str, DeclaredDependency], locked: Mapping[str, LockedDependency]
) -> None:
    for name, dep in declared.items():
        lock = locked.get(name)
        if lock and lock.version != dep.version:
            raise CobraDependencyError(
                f"Conflicto de versión para {name}: cobra.toml declara {dep.version}, "
                f"pero cobra.lock fija {lock.version}."
            )
