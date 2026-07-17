"""Lectura y escritura validada de ``cobra.lock``.

La versión 1 se conserva como formato de intercambio legado; la versión 2
mantiene los metadatos necesarios para resolver un paquete sin consultar la red.
"""

from __future__ import annotations

from dataclasses import dataclass, field
import json
from pathlib import Path
import re
import tomllib
from typing import Any, Mapping, Sequence

from pcobra.cobra.hub.errors import PackageResolutionError
from pcobra.cobra.hub.integrity import normalize_sha256
from pcobra.cobra.hub.models import (
    CobraHubResolution,
    LockedDependency,
    PackageDistribution,
    PackageExtension,
    SUPPORTED_ARCHITECTURES,
    SUPPORTED_DISTRIBUTION_TYPES,
    SUPPORTED_PLATFORMS,
    validate_version_constraint,
)
from pcobra.cobra.packaging import normalizar_nombre_paquete, validar_version_paquete

LOCKFILE_V1 = 1
LOCKFILE_V2 = 2
_KNOWN_VERSIONS = frozenset({LOCKFILE_V1, LOCKFILE_V2})
_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
_PROVIDER_SOURCES = frozenset({"installer-cache", "cobrahub", "cobrahub-cache"})
_V2_ENTRY_KEYS = frozenset(
    {
        "name",
        "version",
        "source",
        "sha256",
        "package_type",
        "requires_cobra",
        "artifact_type",
        "artifact",
        "exports",
        "capabilities",
        "extensions",
        "platforms",
        "architectures",
        "distributions",
        "dependencies",
    }
)


@dataclass(frozen=True)
class LockfileEntryV1:
    """Entrada histórica mínima de un lockfile v1."""

    name: str
    version: str
    source: str | None = None
    sha256: str | None = None


@dataclass(frozen=True)
class LockfileEntryV2(LockfileEntryV1):
    """Entrada v2 autocontenida, apta para resolución offline."""

    package_type: str | None = None
    requires_cobra: str | None = None
    artifact_type: str | None = None
    artifact: str | None = None
    exports: tuple[str, ...] = ()
    capabilities: tuple[str, ...] = ()
    extensions: tuple[Mapping[str, Any], ...] = ()
    platforms: tuple[str, ...] = ()
    architectures: tuple[str, ...] = ()
    distributions: tuple[Mapping[str, Any], ...] = ()
    dependencies: Mapping[str, str] = field(default_factory=dict)


def read_lockfile(path: str | Path) -> dict[str, LockedDependency]:
    """Lee JSON/TOML v1 o v2 y devuelve entradas normalizadas."""

    lock_path = Path(path)
    try:
        text = lock_path.read_text(encoding="utf-8")
    except OSError as exc:
        raise PackageResolutionError(f"No se pudo leer cobra.lock: {exc}") from exc
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        try:
            data = tomllib.loads(text)
        except tomllib.TOMLDecodeError as exc:
            raise PackageResolutionError(
                f"cobra.lock no es JSON ni TOML válido: {exc}"
            ) from exc

    version, entries = _extract_entries(data)
    locked: dict[str, LockedDependency] = {}
    for raw in entries:
        entry = _parse_entry(raw, version, lock_path.parent)
        if entry.name in locked:
            raise PackageResolutionError(
                f"cobra.lock contiene el paquete duplicado {entry.name}."
            )
        metadata = _v2_metadata(entry) if isinstance(entry, LockfileEntryV2) else {}
        locked[entry.name] = LockedDependency(
            name=entry.name,
            version=entry.version,
            source=entry.source,
            sha256=entry.sha256,
            metadata=metadata,
        )
    return locked


def write_lockfile(
    path: str | Path,
    resolved: Mapping[str, CobraHubResolution | LockedDependency],
    *,
    version: int = LOCKFILE_V2,
) -> None:
    """Escribe JSON determinista; ``version=1`` habilita compatibilidad legacy."""

    if type(version) is not int or version not in _KNOWN_VERSIONS:
        raise PackageResolutionError(
            f"Versión de cobra.lock no soportada: {version!r}."
        )
    try:
        entries = [_entry_from_resolution(item, version) for item in resolved.values()]
    except (TypeError, ValueError) as exc:
        raise PackageResolutionError(f"Entrada inválida en cobra.lock: {exc}") from exc
    entries.sort(key=_sort_key)
    payload = {"version": version, "packages": [_entry_dict(item) for item in entries]}
    try:
        Path(path).write_text(
            json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=True) + "\n",
            encoding="utf-8",
        )
    except OSError as exc:
        raise PackageResolutionError(f"No se pudo escribir cobra.lock: {exc}") from exc


def _extract_entries(data: Any) -> tuple[int, Sequence[Any]]:
    if isinstance(data, list):
        return LOCKFILE_V1, data
    if not isinstance(data, Mapping):
        raise PackageResolutionError("cobra.lock debe ser una lista o una tabla.")
    raw_version = data.get("version", LOCKFILE_V1)
    if type(raw_version) is not int or raw_version not in _KNOWN_VERSIONS:
        raise PackageResolutionError(
            f"Versión de esquema de cobra.lock no soportada: {raw_version!r}."
        )
    if "packages" not in data:
        raise PackageResolutionError("cobra.lock no contiene la estructura packages.")
    packages = data["packages"]
    if isinstance(packages, list):
        return raw_version, packages
    if isinstance(packages, Mapping):
        expanded = []
        for name, value in packages.items():
            if isinstance(value, Mapping):
                expanded.append({"name": name, **value})
            else:
                expanded.append({"name": name, "version": value})
        return raw_version, expanded
    raise PackageResolutionError("packages debe ser una lista o una tabla.")


def _parse_entry(raw: Any, version: int, base_dir: Path) -> LockfileEntryV1:
    if not isinstance(raw, Mapping):
        raise PackageResolutionError("cobra.lock contiene una entrada no válida.")
    try:
        name_value = raw.get("name")
        version_value = raw.get("version")
        if not isinstance(name_value, str) or not name_value.strip():
            raise ValueError("name debe ser una cadena no vacía")
        if not isinstance(version_value, str) or not version_value.strip():
            raise ValueError("version debe ser una cadena no vacía")
        name = normalizar_nombre_paquete(name_value)
        package_version = validar_version_paquete(version_value)
        sha256 = _optional_hash(raw)
        source = _optional_string(raw.get("source"), "source")
        source = _resolve_source(source, base_dir)
        if version == LOCKFILE_V1:
            return LockfileEntryV1(name, package_version, source, sha256)
        unknown_keys = set(raw) - _V2_ENTRY_KEYS
        if unknown_keys:
            raise ValueError(
                "claves v2 desconocidas: " + ", ".join(sorted(unknown_keys))
            )
        artifact_type = _optional_string(raw.get("artifact_type"), "artifact_type")
        if (
            artifact_type is not None
            and artifact_type not in SUPPORTED_DISTRIBUTION_TYPES
        ):
            raise ValueError(f"artifact_type no soportado: {artifact_type}")
        return LockfileEntryV2(
            name=name,
            version=package_version,
            source=source,
            sha256=sha256,
            package_type=_optional_string(raw.get("package_type"), "package_type"),
            requires_cobra=_optional_version_constraint(raw.get("requires_cobra")),
            artifact_type=artifact_type,
            artifact=_artifact(raw.get("artifact")),
            exports=_unique_string_tuple(raw.get("exports", []), "exports"),
            capabilities=_unique_string_tuple(
                raw.get("capabilities", []), "capabilities"
            ),
            extensions=_extensions(raw.get("extensions", [])),
            platforms=_supported_values(
                raw.get("platforms", []), "platforms", SUPPORTED_PLATFORMS
            ),
            architectures=_supported_values(
                raw.get("architectures", []),
                "architectures",
                SUPPORTED_ARCHITECTURES,
            ),
            distributions=_distributions(raw.get("distributions", [])),
            dependencies=_dependencies(raw.get("dependencies", {})),
        )
    except (TypeError, ValueError) as exc:
        raise PackageResolutionError(f"Entrada inválida en cobra.lock: {exc}") from exc


def _optional_hash(raw: Mapping[str, Any]) -> str | None:
    keys = [key for key in ("sha256", "checksum", "hash") if key in raw]
    if not keys:
        return None
    value = raw[keys[0]]
    if not isinstance(value, str):
        raise ValueError("sha256 debe ser una cadena")
    value = normalize_sha256(value)
    if not _SHA256_RE.fullmatch(value):
        raise ValueError("sha256 no es un hash SHA-256 válido")
    return value


def _optional_string(value: Any, field_name: str) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str) or not value:
        raise ValueError(f"{field_name} debe ser una cadena no vacía")
    return value


def _optional_version_constraint(value: Any) -> str | None:
    if value is None:
        return None
    return validate_version_constraint(value, "requires_cobra")


def _string_tuple(value: Any, field_name: str) -> tuple[str, ...]:
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        raise ValueError(f"{field_name} debe ser una lista de cadenas")
    return tuple(value)


def _unique_string_tuple(value: Any, field_name: str) -> tuple[str, ...]:
    values = _string_tuple(value, field_name)
    if not all(values):
        raise ValueError(f"{field_name} debe contener cadenas no vacías")
    if len(values) != len(set(values)):
        raise ValueError(f"{field_name} no admite valores duplicados")
    return values


def _supported_values(
    value: Any, field_name: str, supported: frozenset[str]
) -> tuple[str, ...]:
    values = _unique_string_tuple(value, field_name)
    invalid = set(values) - supported
    if invalid:
        raise ValueError(
            f"{field_name} contiene valores no soportados: "
            + ", ".join(sorted(invalid))
        )
    return values


def _artifact(value: Any) -> str | None:
    artifact = _optional_string(value, "artifact")
    if artifact is None:
        return None
    # PackageDistribution es el contrato normativo para rutas de artefactos.
    return PackageDistribution.from_dict(
        {"type": "cobra-package", "path": artifact}
    ).path


def _extensions(value: Any) -> tuple[Mapping[str, Any], ...]:
    mappings = _mapping_tuple(value, "extensions")
    return tuple(PackageExtension.from_dict(item).as_dict() for item in mappings)


def _distributions(value: Any) -> tuple[Mapping[str, Any], ...]:
    mappings = _mapping_tuple(value, "distributions")
    return tuple(PackageDistribution.from_dict(item).as_dict() for item in mappings)


def _mapping_tuple(value: Any, field_name: str) -> tuple[Mapping[str, Any], ...]:
    if not isinstance(value, list) or not all(
        isinstance(item, Mapping) for item in value
    ):
        raise ValueError(f"{field_name} debe ser una lista de tablas")
    return tuple(dict(item) for item in value)


def _dependencies(value: Any) -> dict[str, str]:
    if not isinstance(value, Mapping):
        raise ValueError("dependencies debe ser una tabla")
    result: dict[str, str] = {}
    for raw_name, raw_version in value.items():
        if not isinstance(raw_name, str) or not isinstance(raw_version, str):
            raise ValueError(
                "dependencies debe relacionar nombres y versiones de texto"
            )
        result[normalizar_nombre_paquete(raw_name)] = validar_version_paquete(
            raw_version
        )
    return result


def _resolve_source(source: str | None, base_dir: Path) -> str | None:
    if source is None or source in _PROVIDER_SOURCES:
        return source
    path = Path(source).expanduser()
    return str((path if path.is_absolute() else base_dir / path).resolve())


def _entry_from_resolution(
    item: CobraHubResolution | LockedDependency, version: int
) -> LockfileEntryV1:
    metadata = dict(item.metadata)
    common = dict(
        name=item.name, version=item.version, source=item.source, sha256=item.sha256
    )
    if version == LOCKFILE_V1:
        return LockfileEntryV1(**common)
    artifact_type = _optional_string(metadata.get("artifact_type"), "artifact_type")
    if artifact_type is not None and artifact_type not in SUPPORTED_DISTRIBUTION_TYPES:
        raise ValueError(f"artifact_type no soportado: {artifact_type}")
    artifact = metadata.get("artifact") or getattr(
        getattr(item, "path", None), "name", None
    )
    return LockfileEntryV2(
        **common,
        package_type=metadata.get("package_type"),
        requires_cobra=_optional_version_constraint(metadata.get("requires_cobra")),
        artifact_type=artifact_type,
        artifact=_artifact(artifact),
        exports=_unique_string_tuple(list(metadata.get("exports", ())), "exports"),
        capabilities=_unique_string_tuple(
            list(metadata.get("capabilities", ())), "capabilities"
        ),
        extensions=_extensions(list(metadata.get("extensions", ()))),
        platforms=_supported_values(
            list(metadata.get("platforms", ())), "platforms", SUPPORTED_PLATFORMS
        ),
        architectures=_supported_values(
            list(metadata.get("architectures", ())),
            "architectures",
            SUPPORTED_ARCHITECTURES,
        ),
        distributions=_distributions(list(metadata.get("distributions", ()))),
        dependencies=dict(
            getattr(item, "dependencies", metadata.get("dependencies", {}))
        ),
    )


def _entry_dict(entry: LockfileEntryV1) -> dict[str, Any]:
    data = {"name": entry.name, "version": entry.version}
    for key in ("source", "sha256"):
        value = getattr(entry, key)
        if value is not None:
            data[key] = value
    if isinstance(entry, LockfileEntryV2):
        for key in ("package_type", "requires_cobra", "artifact_type", "artifact"):
            value = getattr(entry, key)
            if value is not None:
                data[key] = value
        data.update(
            exports=list(entry.exports),
            capabilities=list(entry.capabilities),
            extensions=[dict(item) for item in entry.extensions],
            platforms=list(entry.platforms),
            architectures=list(entry.architectures),
            dependencies=dict(sorted(entry.dependencies.items())),
        )
        if entry.distributions:
            data["distributions"] = [dict(item) for item in entry.distributions]
    return data


def _v2_metadata(entry: LockfileEntryV2) -> dict[str, Any]:
    return {
        key: value
        for key, value in _entry_dict(entry).items()
        if key not in {"name", "version", "source", "sha256"}
    }


def _sort_key(entry: LockfileEntryV1) -> tuple[str, ...]:
    return (
        entry.name,
        entry.version,
        entry.source or "",
        getattr(entry, "package_type", None) or "",
        getattr(entry, "artifact_type", None) or "",
        getattr(entry, "artifact", None) or "",
    )


__all__ = [
    "LOCKFILE_V1",
    "LOCKFILE_V2",
    "LockfileEntryV1",
    "LockfileEntryV2",
    "read_lockfile",
    "write_lockfile",
]
