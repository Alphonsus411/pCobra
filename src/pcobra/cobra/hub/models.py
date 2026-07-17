"""Modelos neutrales compartidos por CobraHub y CobraInstaller."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
import re
from typing import Any, Mapping

from pcobra.cobra.hub.compatibility import (
    validate_version_constraint as _validate_version_constraint,
)

PACKAGE_FORMAT_V2 = "cobra-package-v2"
SUPPORTED_PACKAGE_FORMATS = frozenset({"cobra-package-v1", PACKAGE_FORMAT_V2})
SUPPORTED_DISTRIBUTION_TYPES = frozenset(
    {
        "cobra-package",
        "python-wheel",
        "python-sdist",
        "web-assets",
        "javascript-package",
        "rust-binary",
        "wasm",
        "native-binary",
        "embedded",
    }
)
SUPPORTED_PLATFORMS = frozenset(
    {"any", "linux", "windows", "macos", "android", "ios", "freebsd", "browser"}
)
SUPPORTED_ARCHITECTURES = frozenset(
    {"any", "x86", "x86_64", "armv7", "arm64", "wasm32"}
)

_NAME_RE = re.compile(r"^[a-z0-9](?:[a-z0-9_.-]*[a-z0-9])?$")
_IDENTIFIER_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
_SEMVER_RE = re.compile(
    r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)"
    r"(?:-[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*)?"
    r"(?:\+[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*)?$"
)
_SHA256_RE = re.compile(r"^[0-9a-fA-F]{64}$")
_ENTRYPOINT_RE = re.compile(
    r"^[A-Za-z_][A-Za-z0-9_]*(?:\.[A-Za-z_][A-Za-z0-9_]*)*"
    r":[A-Za-z_][A-Za-z0-9_]*(?:\.[A-Za-z_][A-Za-z0-9_]*)*$"
)


def _object(value: Any, field_name: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ValueError(f"{field_name} debe ser un objeto JSON")
    if not all(isinstance(key, str) for key in value):
        raise ValueError(f"{field_name} solo admite claves de texto")
    return value


def _string(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value:
        raise ValueError(f"{field_name} debe ser una cadena no vacía")
    return value


def _string_list(value: Any, field_name: str) -> tuple[str, ...]:
    if not isinstance(value, list) or not all(
        isinstance(item, str) and item for item in value
    ):
        raise ValueError(f"{field_name} debe ser una lista de cadenas no vacías")
    if len(value) != len(set(value)):
        raise ValueError(f"{field_name} no admite valores duplicados")
    return tuple(value)


def _name(value: Any, field_name: str = "name") -> str:
    text = _string(value, field_name)
    if not _NAME_RE.fullmatch(text) or ".." in text:
        raise ValueError(f"{field_name} inválido")
    return text


def _semver(value: Any, field_name: str) -> str:
    text = _string(value, field_name)
    if not _SEMVER_RE.fullmatch(text):
        raise ValueError(f"{field_name} debe ser una versión SemVer exacta")
    return text


def validate_version_constraint(value: Any, field_name: str) -> str:
    """Valida una intersección estática de comparadores de versión Cobra."""
    return _validate_version_constraint(value, field_name)


def _namespace(value: Any, field_name: str) -> str:
    text = _string(value, field_name)
    if not all(_IDENTIFIER_RE.fullmatch(part) for part in text.split(".")):
        raise ValueError(f"{field_name} debe ser un namespace válido")
    return text


def _path(value: Any, field_name: str) -> str:
    text = _string(value, field_name)
    parts = text.split("/")
    if (
        "\\" in text
        or text.startswith("/")
        or re.match(r"^[A-Za-z]:", text)
        or any(part in {"", ".", ".."} for part in parts)
    ):
        raise ValueError(f"{field_name} contiene una ruta insegura")
    return text


def _enum_list(value: Any, field_name: str, allowed: frozenset[str]) -> tuple[str, ...]:
    values = _string_list(value, field_name)
    invalid = set(values) - allowed
    if invalid:
        raise ValueError(
            f"{field_name} contiene valores no soportados: {', '.join(sorted(invalid))}"
        )
    return values


def _architectures(value: Any, field_name: str) -> tuple[str, ...]:
    """Normaliza el alias histórico ``aarch64`` al valor contractual ``arm64``."""
    values = _string_list(value, field_name)
    allowed = SUPPORTED_ARCHITECTURES | {"aarch64"}
    invalid = set(values) - allowed
    if invalid:
        raise ValueError(
            f"{field_name} contiene valores no soportados: "
            f"{', '.join(sorted(invalid))}"
        )
    normalized = tuple("arm64" if item == "aarch64" else item for item in values)
    if len(normalized) != len(set(normalized)):
        raise ValueError(f"{field_name} no admite valores duplicados")
    return normalized


@dataclass(frozen=True)
class PackageDistribution:
    """Artefacto publicable descrito sin abrirlo ni ejecutar código suyo."""

    type: str
    path: str
    platforms: tuple[str, ...] = ("any",)
    architectures: tuple[str, ...] = ("any",)

    @classmethod
    def from_dict(cls, value: Any) -> "PackageDistribution":
        data = _object(value, "distribution")
        distribution_type = _string(data.get("type"), "distribution.type")
        if distribution_type not in SUPPORTED_DISTRIBUTION_TYPES:
            raise ValueError(f"Tipo de distribución no soportado: {distribution_type}")
        return cls(
            type=distribution_type,
            path=_path(data.get("path"), "distribution.path"),
            platforms=_enum_list(
                data.get("platforms", ["any"]),
                "distribution.platforms",
                SUPPORTED_PLATFORMS,
            ),
            architectures=_architectures(
                data.get("architectures", ["any"]), "distribution.architectures"
            ),
        )

    def as_dict(self) -> dict[str, Any]:
        return {
            "type": self.type,
            "path": self.path,
            "platforms": list(self.platforms),
            "architectures": list(self.architectures),
        }


@dataclass(frozen=True)
class PackageExtension:
    """Declaración estática de una extensión; no resuelve su entrypoint."""

    namespace: str
    provider: str
    capabilities: tuple[str, ...]
    entrypoint: str

    @classmethod
    def from_dict(cls, value: Any) -> "PackageExtension":
        data = _object(value, "extension")
        namespace = _namespace(data.get("namespace"), "extension.namespace")
        provider = _name(data.get("provider"), "extension.provider")
        capabilities = _string_list(data.get("capabilities"), "extension.capabilities")
        if not all(_NAME_RE.fullmatch(item) for item in capabilities):
            raise ValueError("extension.capabilities contiene un nombre inválido")
        entrypoint = _string(data.get("entrypoint"), "extension.entrypoint")
        if not _ENTRYPOINT_RE.fullmatch(entrypoint):
            raise ValueError("extension.entrypoint debe tener formato módulo:objeto")
        return cls(namespace, provider, capabilities, entrypoint)

    def as_dict(self) -> dict[str, Any]:
        return {
            "namespace": self.namespace,
            "provider": self.provider,
            "capabilities": list(self.capabilities),
            "entrypoint": self.entrypoint,
        }


@dataclass(frozen=True)
class PackageManifestV2:
    """Manifiesto Hub v2 validado exclusivamente mediante análisis de datos."""

    format: str
    name: str
    version: str
    package_type: str
    requires_cobra: str
    exports: tuple[str, ...]
    capabilities: tuple[str, ...]
    platforms: tuple[str, ...]
    architectures: tuple[str, ...]
    dependencies: Mapping[str, str]
    distributions: tuple[PackageDistribution, ...]
    extensions: tuple[PackageExtension, ...]
    files: tuple[str, ...]
    checksums: Mapping[str, str]

    @classmethod
    def from_dict(cls, value: Any) -> "PackageManifestV2":
        data = _object(value, "manifest")
        if data.get("format") != PACKAGE_FORMAT_V2:
            raise ValueError(f"Formato de paquete no soportado: {data.get('format')}")
        package_type = _string(data.get("package_type"), "package_type")
        dependencies_data = _object(data.get("dependencies"), "dependencies")
        dependencies = {
            _name(key, "dependency.name"): _semver(version, f"dependencies.{key}")
            for key, version in dependencies_data.items()
        }
        files = _string_list(data.get("files"), "files")
        normalized_files = tuple(_path(item, "files") for item in files)
        checksum_data = _object(data.get("checksums"), "checksums")
        checksums: dict[str, str] = {}
        for raw_path, raw_hash in checksum_data.items():
            file_path = _path(raw_path, "checksums")
            checksum = _string(raw_hash, f"checksums.{raw_path}")
            if not _SHA256_RE.fullmatch(checksum):
                raise ValueError(f"Checksum SHA-256 inválido para {raw_path}")
            checksums[file_path] = checksum.lower()
        if set(normalized_files) != set(checksums):
            raise ValueError(
                "files y checksums deben declarar exactamente las mismas rutas"
            )
        exports = tuple(
            _namespace(item, "exports")
            for item in _string_list(data.get("exports"), "exports")
        )
        capabilities = _string_list(data.get("capabilities"), "capabilities")
        if not all(_NAME_RE.fullmatch(item) for item in capabilities):
            raise ValueError("capabilities contiene un nombre inválido")
        distributions_value = data.get("distributions")
        extensions_value = data.get("extensions")
        if not isinstance(distributions_value, list):
            raise ValueError("distributions debe ser una lista")
        if not isinstance(extensions_value, list):
            raise ValueError("extensions debe ser una lista")
        distributions = tuple(
            PackageDistribution.from_dict(item) for item in distributions_value
        )
        if any(item.path not in normalized_files for item in distributions):
            raise ValueError(
                "Cada distribución debe apuntar a una ruta declarada en files"
            )
        return cls(
            format=PACKAGE_FORMAT_V2,
            name=_name(data.get("name")),
            version=_semver(data.get("version"), "version"),
            package_type=package_type,
            requires_cobra=validate_version_constraint(
                data.get("requires_cobra"), "requires_cobra"
            ),
            exports=exports,
            capabilities=capabilities,
            platforms=_enum_list(
                data.get("platforms"), "platforms", SUPPORTED_PLATFORMS
            ),
            architectures=_architectures(data.get("architectures"), "architectures"),
            dependencies=dependencies,
            distributions=distributions,
            extensions=tuple(
                PackageExtension.from_dict(item) for item in extensions_value
            ),
            files=normalized_files,
            checksums=checksums,
        )

    def as_dict(self) -> dict[str, Any]:
        return {
            "format": self.format,
            "name": self.name,
            "version": self.version,
            "package_type": self.package_type,
            "requires_cobra": self.requires_cobra,
            "exports": list(self.exports),
            "capabilities": list(self.capabilities),
            "platforms": list(self.platforms),
            "architectures": list(self.architectures),
            "dependencies": dict(self.dependencies),
            "distributions": [item.as_dict() for item in self.distributions],
            "extensions": [item.as_dict() for item in self.extensions],
            "files": list(self.files),
            "checksums": dict(self.checksums),
        }


def manifest_v2_from_dict(value: Any) -> PackageManifestV2:
    """Fachada funcional para validar un manifiesto v2 sin cargar entrypoints."""
    return PackageManifestV2.from_dict(value)


def manifest_v2_to_dict(manifest: PackageManifestV2) -> dict[str, Any]:
    return manifest.as_dict()


# Nombres cortos y constantes descriptivas para consumidores que construyen
# catálogos Hub. Los nombres principales permanecen explícitos y estables.
ManifestV2 = PackageManifestV2
DistributionV2 = PackageDistribution
ExtensionV2 = PackageExtension
PACKAGE_FORMATS = SUPPORTED_PACKAGE_FORMATS
DISTRIBUTION_TYPES = SUPPORTED_DISTRIBUTION_TYPES
PLATFORMS = SUPPORTED_PLATFORMS
ARCHITECTURES = SUPPORTED_ARCHITECTURES


@dataclass(frozen=True)
class CobraHubResolution:
    """Paquete Cobra localizado, validado y acompañado de metadatos Hub v2."""

    name: str
    version: str
    path: Path
    sha256: str
    source: str
    dependencies: dict[str, str] = field(default_factory=dict)
    metadata: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class DeclaredDependency:
    """Dependencia declarada por el usuario en ``cobra.toml``."""

    name: str
    version: str
    source: str | None = None
    metadata: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class LockedDependency:
    """Entrada normalizada procedente de ``cobra.lock``."""

    name: str
    version: str
    sha256: str | None = None
    source: str | None = None
    metadata: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class DependencyResolutionResult:
    """Resultado enriquecido v2 de resolver el grafo de un proyecto."""

    declared: dict[str, DeclaredDependency]
    used_imports: set[str]
    resolved: dict[str, CobraHubResolution]
    lockfile_path: Path
    lockfile_created: bool = False
    conflicts: tuple[str, ...] = ()
    missing_declarations: tuple[str, ...] = ()
    dependency_chains: Mapping[str, str] = field(default_factory=dict)
    metadata: Mapping[str, Any] = field(default_factory=dict)
