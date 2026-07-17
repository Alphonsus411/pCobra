"""Localización de paquetes CobraHub para el instalador Cobra.

Reutiliza ``pcobra.cobra.hub.repository`` y ``pcobra.cobra.packaging`` para
buscar en caché, descargar, inspeccionar y validar artefactos ``.co``.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from pcobra.cobra.hub.repository import PackageRepository
from pcobra.cobra.hub.cache import CobraInstallerCache
from pcobra.cobra.hub.integrity import normalize_sha256, sha256_file
from pcobra.cobra.hub.models import CobraHubResolution
from pcobra.cobra_installer.project import CobraInstallerError
from pcobra.cobra.packaging import (
    es_paquete_cobra,
    inspeccionar_paquete,
    normalizar_nombre_paquete,
    validar_paquete,
    validar_version_paquete,
)

__all__ = ["CobraInstallerError", "CobraHubResolution", "CobraHubResolver"]



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
    ) -> CobraHubResolution:
        """Localiza/descarga ``name`` y valida versión, formato e integridad."""

        normalized_name = self._name(name)
        normalized_version = self._version(version, normalized_name)
        if expected_sha256:
            expected_sha256 = normalize_sha256(expected_sha256)

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
                )

        if self.repository is None:
            raise CobraInstallerError(
                f"Dependencia Cobra no encontrada en caché: {normalized_name}=={normalized_version}. "
                "Configure CobraHub o precargue el paquete en la caché local."
            )

        try:
            downloaded = self.repository.download(normalized_name, normalized_version)
        except Exception as exc:  # noqa: BLE001 - se traduce a error controlado
            raise CobraInstallerError(
                f"No se pudo descargar {normalized_name}=={normalized_version} desde CobraHub: {exc}"
            ) from exc
        return self._inspect_candidate(
            downloaded.path,
            normalized_name,
            normalized_version,
            expected_sha256=expected_sha256 or downloaded.checksum,
            source="cobrahub",
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
    ) -> CobraHubResolution:
        try:
            if not es_paquete_cobra(path):
                raise ValueError("el artefacto no es un paquete Cobra .co válido")
            validation = validar_paquete(path)
            inspection = inspeccionar_paquete(path)
        except Exception as exc:  # noqa: BLE001 - se traduce a error controlado
            raise CobraInstallerError(
                f"Paquete Cobra inválido para {name}: {exc}"
            ) from exc

        manifest = validation.manifest
        package_name = self._name(str(manifest.get("name", "")))
        package_version = self._version(str(manifest.get("version", "")), package_name)
        if package_name != name:
            raise CobraInstallerError(
                f"Paquete incorrecto: se esperaba {name}, pero el artefacto declara {package_name}."
            )
        if package_version != version:
            raise CobraInstallerError(
                f"Versión incorrecta para {name}: se esperaba {version}, pero el artefacto declara {package_version}."
            )

        digest = inspection.checksum or self._sha256_file(path)
        if expected_sha256 and digest.lower() != expected_sha256.lower():
            raise CobraInstallerError(
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
        return CobraHubResolution(
            name=package_name,
            version=package_version,
            path=Path(path),
            sha256=digest,
            source=source,
            dependencies=dependencies,
        )

    _sha256_file = staticmethod(sha256_file)

    @staticmethod
    def _name(name: str) -> str:
        try:
            return normalizar_nombre_paquete(name)
        except ValueError as exc:
            raise CobraInstallerError(
                f"Nombre de paquete Cobra inválido: {name}"
            ) from exc

    @staticmethod
    def _version(version: str, name: str) -> str:
        try:
            return validar_version_paquete(version)
        except ValueError as exc:
            raise CobraInstallerError(
                f"Versión inválida para {name}: {version}"
            ) from exc
