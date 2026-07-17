"""Localización de paquetes CobraHub para el instalador Cobra.

Reutiliza ``pcobra.cobra.hub.repository`` y ``pcobra.cobra.packaging`` para
buscar en caché, descargar, inspeccionar y validar artefactos ``.co``.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from pcobra.cobra.hub.errors import (
    CobraHubError,
    PackageCompatibilityError,
    PackageIntegrityError,
    PackageNotFoundError,
    PackageProviderError,
    PackageResolutionError,
)
from pcobra.cobra.hub.repository import PackageRepository
from pcobra.cobra.hub.cache import CobraInstallerCache
from pcobra.cobra.hub.integrity import normalize_sha256, sha256_file
from pcobra.cobra.hub.models import (
    PACKAGE_FORMAT_V2,
    CobraHubResolution,
    PackageDistribution,
    manifest_v2_from_dict,
)
from pcobra.cobra.hub.providers.local import LocalArtifactProvider
from pcobra.cobra.packaging import (
    es_paquete_cobra,
    inspeccionar_paquete,
    normalizar_nombre_paquete,
    validar_paquete,
    validar_version_paquete,
)

__all__ = ["CobraHubResolution", "CobraHubResolver"]


class CobraHubResolver:
    """Resuelve paquetes desde caché local, ruta explícita o repositorio CobraHub."""

    def __init__(
        self,
        repository: PackageRepository | None = None,
        *,
        cache_dir: str | Path | None = None,
    ) -> None:
        self.repository = repository
        self.cache = CobraInstallerCache(cache_dir=cache_dir)
        self.cache_dir = self.cache.cache_dir

    def resolve(
        self,
        name: str,
        version: str,
        *,
        expected_sha256: str | None = None,
        source: str | None = None,
        platform: str = "any",
        architecture: str = "any",
    ) -> CobraHubResolution:
        """Localiza/descarga ``name`` y valida versión, formato e integridad."""

        normalized_name = self._name(name)
        normalized_version = self._version(version, normalized_name)
        if expected_sha256:
            try:
                expected_sha256 = normalize_sha256(expected_sha256)
            except ValueError as exc:
                raise PackageIntegrityError(str(exc)) from exc

        if source and source not in {"installer-cache", "cobrahub", "cobrahub-cache"}:
            try:
                artifact = LocalArtifactProvider(
                    source, cache_dir=self.cache_dir
                ).acquire(
                    normalized_name,
                    normalized_version,
                    expected_sha256=expected_sha256,
                )
            except CobraHubError:
                raise
            except Exception as exc:  # noqa: BLE001 - frontera con proveedor externo
                raise PackageProviderError(str(exc)) from exc
            return self._inspect_candidate(
                artifact.path,
                normalized_name,
                normalized_version,
                expected_sha256=expected_sha256,
                source=str(Path(source).expanduser().resolve()),
                platform=platform,
                architecture=architecture,
            )

        candidates: list[Path] = []
        if source:
            source_path = Path(source).expanduser()
            if source_path.exists():
                candidates.append(source_path)
        candidates.extend(self._cache_candidates(normalized_name, normalized_version))

        for candidate in candidates:
            if candidate.is_file():
                cache_entry = self.cache.validate(
                    candidate, normalized_name, normalized_version
                )
                return self._inspect_candidate(
                    candidate,
                    normalized_name,
                    normalized_version,
                    expected_sha256=expected_sha256,
                    source=cache_entry.source if cache_entry else str(candidate),
                    platform=platform,
                    architecture=architecture,
                )

        if self.repository is None:
            raise PackageNotFoundError(
                f"Dependencia Cobra no encontrada en caché: {normalized_name}=={normalized_version}. "
                "Configure CobraHub o precargue el paquete en la caché local."
            )

        try:
            downloaded = self.repository.download(normalized_name, normalized_version)
        except CobraHubError:
            raise
        except FileNotFoundError as exc:
            raise PackageNotFoundError(
                f"No se encontró {normalized_name}=={normalized_version} en CobraHub: {exc}"
            ) from exc
        except Exception as exc:  # noqa: BLE001 - frontera con repositorio externo
            raise PackageProviderError(
                f"No se pudo descargar {normalized_name}=={normalized_version} desde CobraHub: {exc}"
            ) from exc
        return self._inspect_candidate(
            downloaded.path,
            normalized_name,
            normalized_version,
            expected_sha256=expected_sha256 or downloaded.checksum,
            source="cobrahub",
            platform=platform,
            architecture=architecture,
        )

    def _cache_candidates(self, name: str, version: str) -> list[Path]:
        return self.cache.candidates(name, version)

    def _inspect_candidate(
        self,
        path: Path,
        name: str,
        version: str,
        *,
        expected_sha256: str | None,
        source: str,
        platform: str = "any",
        architecture: str = "any",
    ) -> CobraHubResolution:
        try:
            if not es_paquete_cobra(path):
                raise ValueError("el artefacto no es un paquete Cobra .co válido")
            validation = validar_paquete(path)
            inspection = inspeccionar_paquete(path)
        except CobraHubError:
            raise
        except Exception as exc:  # noqa: BLE001 - valida una distribución externa
            raise PackageCompatibilityError(
                f"Paquete Cobra inválido para {name}: {exc}"
            ) from exc

        manifest = validation.manifest
        package_name = self._name(str(manifest.get("name", "")))
        package_version = self._version(str(manifest.get("version", "")), package_name)
        if package_name != name:
            raise PackageCompatibilityError(
                f"Paquete incorrecto: se esperaba {name}, pero el artefacto declara {package_name}."
            )
        if package_version != version:
            raise PackageCompatibilityError(
                f"Versión incorrecta para {name}: se esperaba {version}, pero el artefacto declara {package_version}."
            )

        digest = inspection.checksum or self._sha256_file(path)
        if expected_sha256 and digest.lower() != expected_sha256.lower():
            raise PackageIntegrityError(
                f"Hash inválido para {name}=={version}: se esperaba {expected_sha256}, se obtuvo {digest}."
            )

        raw_deps = manifest.get("dependencies") or {}
        dependencies = (
            {
                self._name(str(dep_name)): self._version(
                    str(dep_version), str(dep_name)
                )
                for dep_name, dep_version in raw_deps.items()
            }
            if isinstance(raw_deps, dict)
            else {}
        )
        metadata: dict[str, Any] = {}
        if manifest.get("format") == PACKAGE_FORMAT_V2:
            try:
                manifest_v2 = manifest_v2_from_dict(manifest)
                distribution = self._select_distribution(
                    manifest_v2.distributions, platform, architecture
                )
            except PackageCompatibilityError:
                raise
            except (TypeError, ValueError) as exc:
                raise PackageCompatibilityError(
                    f"Manifiesto v2 incompatible para {name}: {exc}"
                ) from exc
            metadata = {
                "package_type": manifest_v2.package_type,
                "requires_cobra": manifest_v2.requires_cobra,
                "exports": list(manifest_v2.exports),
                "capabilities": list(manifest_v2.capabilities),
                "extensions": [item.as_dict() for item in manifest_v2.extensions],
                "platforms": list(manifest_v2.platforms),
                "architectures": list(manifest_v2.architectures),
                "distributions": [item.as_dict() for item in manifest_v2.distributions],
                "artifact_type": distribution.type,
                "artifact": distribution.path,
            }
        return CobraHubResolution(
            name=package_name,
            version=package_version,
            path=Path(path),
            sha256=digest,
            source=source,
            dependencies=dependencies,
            metadata=metadata,
        )

    @staticmethod
    def _select_distribution(
        distributions: tuple[PackageDistribution, ...],
        platform: str,
        architecture: str,
    ) -> PackageDistribution:
        """Elige un artefacto compatible e instalable sin ejecutar su código."""

        compatible = [
            item
            for item in distributions
            if (
                platform == "any"
                or "any" in item.platforms
                or platform in item.platforms
            )
            and (
                architecture == "any"
                or "any" in item.architectures
                or architecture in item.architectures
            )
        ]
        if not compatible:
            raise PackageCompatibilityError(
                "No hay una distribución compatible con la plataforma "
                f"{platform!r} y la arquitectura {architecture!r}."
            )

        for distribution in compatible:
            if distribution.type == "cobra-package":
                return distribution

        found_types = ", ".join(
            repr(item)
            for item in sorted({distribution.type for distribution in compatible})
        )
        if len(compatible) == 1:
            raise PackageCompatibilityError(
                "La distribución compatible es de tipo "
                f"{found_types}; este tipo todavía no es instalable."
            )
        raise PackageCompatibilityError(
            f"Las distribuciones compatibles tienen los tipos {found_types}; "
            "estos tipos todavía no son instalables."
        )

    _sha256_file = staticmethod(sha256_file)

    @staticmethod
    def _name(name: str) -> str:
        try:
            return normalizar_nombre_paquete(name)
        except ValueError as exc:
            raise PackageResolutionError(
                f"Nombre de paquete Cobra inválido: {name}"
            ) from exc

    @staticmethod
    def _version(version: str, name: str) -> str:
        try:
            return validar_version_paquete(version)
        except ValueError as exc:
            raise PackageResolutionError(
                f"Versión inválida para {name}: {version}"
            ) from exc
