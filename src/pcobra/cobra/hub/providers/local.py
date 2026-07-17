"""Proveedor offline de artefactos Cobra almacenados en el sistema local."""

from __future__ import annotations

import os
import shutil
import tempfile
from pathlib import Path

from pcobra.cobra.hub.errors import (
    PackageIntegrityError,
    PackageNotFoundError,
    PackageResolutionError,
)
from pcobra.cobra.hub.integrity import normalize_sha256, sha256_file
from pcobra.cobra.hub.repository import DownloadedPackage, package_cache_dir
from pcobra.cobra.packaging import (
    inspeccionar_paquete,
    normalizar_nombre_paquete,
    validar_paquete,
    validar_version_paquete,
)


class LocalArtifactProvider:
    """Localiza, valida y cachea un ``.co`` desde un archivo o directorio."""

    def __init__(
        self, source: str | Path, *, cache_dir: str | Path | None = None
    ) -> None:
        self.source = Path(source).expanduser().resolve()
        self.cache_dir = (
            Path(cache_dir).expanduser() if cache_dir else package_cache_dir()
        )
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def acquire(
        self,
        name: str,
        version: str | None = None,
        *,
        expected_sha256: str | None = None,
    ) -> DownloadedPackage:
        normalized_name = normalizar_nombre_paquete(name)
        normalized_version = validar_version_paquete(version or "")
        expected = normalize_sha256(expected_sha256)
        candidate = self._locate(normalized_name, normalized_version)
        digest = sha256_file(candidate)
        if expected and digest != expected:
            raise PackageIntegrityError(
                f"Hash inválido para {normalized_name}=={normalized_version}: "
                f"se esperaba {expected}, se obtuvo {digest}."
            )

        target = self.cache_dir / f"{normalized_name}-{normalized_version}-{digest}.co"
        if not target.is_file():
            fd, partial_name = tempfile.mkstemp(
                prefix=f".{target.name}.", suffix=".partial", dir=self.cache_dir
            )
            os.close(fd)
            partial = Path(partial_name)
            try:
                shutil.copyfile(candidate, partial)
                self._validate_identity(partial, normalized_name, normalized_version)
                if sha256_file(partial) != digest:
                    raise PackageIntegrityError(
                        "El artefacto cambió mientras se copiaba."
                    )
                os.replace(partial, target)
            finally:
                partial.unlink(missing_ok=True)
        else:
            self._validate_identity(target, normalized_name, normalized_version)
            if sha256_file(target) != digest:
                raise PackageIntegrityError(
                    "La entrada reutilizada de caché está corrupta."
                )
        return DownloadedPackage(
            path=target,
            name=normalized_name,
            version=normalized_version,
            checksum=digest,
        )

    def verify(self, artifact: DownloadedPackage) -> bool:
        try:
            self._validate_identity(
                artifact.path,
                normalizar_nombre_paquete(artifact.name),
                validar_version_paquete(artifact.version or ""),
            )
            return not artifact.checksum or sha256_file(
                artifact.path
            ) == normalize_sha256(artifact.checksum)
        except (OSError, ValueError, PackageResolutionError):
            return False

    def _locate(self, name: str, version: str) -> Path:
        if not self.source.exists():
            raise PackageNotFoundError(f"La ruta local no existe: {self.source}")
        if self.source.is_file():
            if self.source.suffix != ".co":
                raise PackageResolutionError(
                    f"La ruta local no es un artefacto .co: {self.source}"
                )
            self._validate_identity(self.source, name, version)
            return self.source
        if not self.source.is_dir():
            raise PackageResolutionError(
                f"La ruta local no es archivo ni directorio: {self.source}"
            )

        matches: list[Path] = []
        invalid: list[str] = []
        for path in sorted(self.source.glob("*.co"), key=lambda item: item.name):
            try:
                self._validate_identity(path, name, version)
            except PackageResolutionError as exc:
                invalid.append(str(exc))
            else:
                matches.append(path)
        if len(matches) > 1:
            raise PackageResolutionError(
                f"Directorio local ambiguo para {name}=={version}: "
                + ", ".join(path.name for path in matches)
            )
        if not matches:
            detail = f" ({'; '.join(invalid)})" if invalid else ""
            raise PackageNotFoundError(
                f"No se encontró {name}=={version} en {self.source}{detail}"
            )
        return matches[0]

    @staticmethod
    def _validate_identity(path: Path, name: str, version: str) -> None:
        try:
            inspection = validar_paquete(path)
            manifest = inspection.manifest
            actual_name = normalizar_nombre_paquete(str(manifest.get("name", "")))
            actual_version = validar_version_paquete(str(manifest.get("version", "")))
            # Fuerza también la lectura estructural usada por el Hub.
            inspeccionar_paquete(path)
        except (OSError, ValueError) as exc:
            raise PackageResolutionError(
                f"Artefacto local inválido {path}: {exc}"
            ) from exc
        if actual_name != name or actual_version != version:
            raise PackageResolutionError(
                f"Artefacto discordante {path}: declara {actual_name}=={actual_version}; "
                f"se esperaba {name}=={version}."
            )


__all__ = ["LocalArtifactProvider"]
