"""Caché de artefactos de build para CobraInstaller.

La caché del instalador reutiliza la caché local de CobraHub como fuente
principal para paquetes ``.co`` ya descargados, pero escribe artefactos propios en
un subdirectorio separado. Así se evitan escrituras accidentales dentro del
proyecto: el instalador solo debe tocar el árbol del usuario cuando genera de
forma explícita ``cobra.lock``.
"""

from __future__ import annotations

import hashlib
import os
import shutil
from dataclasses import dataclass
from pathlib import Path

from pcobra.cobra.hub.repository import package_cache_dir
from pcobra.cobra.packaging import normalizar_nombre_paquete, validar_version_paquete

__all__ = [
    "COBRA_INSTALLER_CACHE_DIR_ENV",
    "CobraInstallerCache",
    "CobraInstallerCacheEntry",
    "installer_cache_dir",
]

COBRA_INSTALLER_CACHE_DIR_ENV = "COBRA_INSTALLER_CACHE_DIR"
_INSTALLER_CACHE_SUBDIR = "cobra-installer"


@dataclass(frozen=True)
class CobraInstallerCacheEntry:
    """Artefacto localizado en una de las capas de caché."""

    name: str
    version: str
    path: Path
    sha256: str
    source: str


class CobraInstallerCache:
    """Caché en capas para artefactos de CobraInstaller.

    Prioridad de lectura:
    1. Caché existente de CobraHub, salvo que se configure explícitamente un
       directorio de instalador mediante ``COBRA_INSTALLER_CACHE_DIR`` o
       ``cache_dir``.
    2. Subdirectorio propio de CobraInstaller para artefactos temporales.

    Las escrituras de :meth:`put` siempre van a la capa propia del instalador y
    nunca al directorio del proyecto.
    """

    def __init__(
        self,
        *,
        cache_dir: str | Path | None = None,
        hub_cache_dir: str | Path | None = None,
    ) -> None:
        env_cache_dir = os.environ.get(COBRA_INSTALLER_CACHE_DIR_ENV)
        self._explicit_installer_cache = cache_dir is not None or bool(env_cache_dir)
        self.hub_cache_dir = (
            Path(hub_cache_dir).expanduser() if hub_cache_dir else package_cache_dir()
        )
        self.cache_dir = installer_cache_dir(cache_dir, hub_cache_dir=self.hub_cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def get(
        self,
        name: str,
        version: str,
        *,
        expected_sha256: str | None = None,
    ) -> CobraInstallerCacheEntry | None:
        """Devuelve un artefacto válido o ``None`` si no está cacheado.

        ``expected_sha256`` permite invalidar automáticamente copias obsoletas o
        corruptas por hash. La versión forma parte del nombre canónico del
        artefacto, por lo que pedir otra versión no reutiliza una entrada previa.
        """

        normalized_name, normalized_version = self._normalize_key(name, version)
        expected_sha256 = self._normalize_hash(expected_sha256)
        for candidate, source in self._candidates(normalized_name, normalized_version):
            if not candidate.is_file():
                continue
            entry = self.validate(
                candidate,
                normalized_name,
                normalized_version,
                expected_sha256=expected_sha256,
                source=source,
            )
            if entry is not None:
                return entry
            if source == "installer-cache":
                candidate.unlink(missing_ok=True)
        return None

    def put(
        self,
        name: str,
        version: str,
        artifact: str | Path,
        *,
        expected_sha256: str | None = None,
    ) -> CobraInstallerCacheEntry:
        """Copia ``artifact`` a la caché propia del instalador y lo valida."""

        normalized_name, normalized_version = self._normalize_key(name, version)
        expected_sha256 = self._normalize_hash(expected_sha256)
        source_path = Path(artifact).expanduser()
        target = self.cache_dir / self._filename(normalized_name, normalized_version)
        if source_path.resolve() != target.resolve():
            shutil.copy2(source_path, target)
        entry = self.validate(
            target,
            normalized_name,
            normalized_version,
            expected_sha256=expected_sha256,
            source="installer-cache",
        )
        if entry is None:
            target.unlink(missing_ok=True)
            raise ValueError(
                f"Artefacto inválido para {normalized_name}=={normalized_version}"
            )
        return entry

    def validate(
        self,
        artifact: str | Path,
        name: str,
        version: str,
        *,
        expected_sha256: str | None = None,
        source: str | None = None,
    ) -> CobraInstallerCacheEntry | None:
        """Valida ruta, versión y hash de un artefacto cacheado."""

        normalized_name, normalized_version = self._normalize_key(name, version)
        path = Path(artifact).expanduser()
        if not path.is_file():
            return None
        if path.name not in {
            self._filename(normalized_name, normalized_version),
            f"{normalized_name}.co",
        }:
            return None
        digest = self._sha256_file(path)
        expected_sha256 = self._normalize_hash(expected_sha256)
        if expected_sha256 and digest.lower() != expected_sha256.lower():
            return None
        return CobraInstallerCacheEntry(
            name=normalized_name,
            version=normalized_version,
            path=path,
            sha256=digest,
            source=source or self._source_for(path),
        )

    def clear(self, name: str | None = None, version: str | None = None) -> int:
        """Elimina artefactos de la caché propia del instalador.

        No limpia la caché compartida de CobraHub para no borrar paquetes que
        puedan estar siendo usados por otros comandos.
        """

        deleted = 0
        for path in self.cache_dir.glob("*.co"):
            if not self._matches(path, name=name, version=version):
                continue
            path.unlink(missing_ok=True)
            deleted += 1
        return deleted

    def candidates(self, name: str, version: str) -> list[Path]:
        """Lista rutas candidatas en orden de prioridad de lectura."""

        normalized_name, normalized_version = self._normalize_key(name, version)
        return [
            path
            for path, _source in self._candidates(normalized_name, normalized_version)
        ]

    def _candidates(self, name: str, version: str) -> list[tuple[Path, str]]:
        installer_candidates = [
            (self.cache_dir / self._filename(name, version), "installer-cache"),
            (self.cache_dir / f"{name}.co", "installer-cache"),
        ]
        if self._explicit_installer_cache:
            return installer_candidates
        return [
            (self.hub_cache_dir / self._filename(name, version), "cobrahub-cache"),
            (self.hub_cache_dir / f"{name}.co", "cobrahub-cache"),
            *installer_candidates,
        ]

    def _source_for(self, path: Path) -> str:
        try:
            if path.resolve().parent == self.hub_cache_dir.resolve():
                return "cobrahub-cache"
            if path.resolve().parent == self.cache_dir.resolve():
                return "installer-cache"
        except OSError:
            pass
        return str(path)

    @staticmethod
    def _filename(name: str, version: str) -> str:
        return f"{name}-{version}.co"

    @staticmethod
    def _normalize_key(name: str, version: str) -> tuple[str, str]:
        return normalizar_nombre_paquete(name), validar_version_paquete(version)

    @staticmethod
    def _normalize_hash(value: str | None) -> str | None:
        return value.removeprefix("sha256:").lower() if value else None

    @staticmethod
    def _sha256_file(path: Path) -> str:
        sha = hashlib.sha256()
        with path.open("rb") as fh:
            for chunk in iter(lambda: fh.read(1024 * 1024), b""):
                sha.update(chunk)
        return sha.hexdigest()

    def _matches(self, path: Path, *, name: str | None, version: str | None) -> bool:
        if name is None:
            return True
        normalized_name = normalizar_nombre_paquete(name)
        if version is None:
            return path.name == f"{normalized_name}.co" or path.name.startswith(
                f"{normalized_name}-"
            )
        normalized_version = validar_version_paquete(version)
        return path.name == self._filename(normalized_name, normalized_version)


def installer_cache_dir(
    cache_dir: str | Path | None = None,
    *,
    hub_cache_dir: str | Path | None = None,
) -> Path:
    """Devuelve el directorio de caché propio de CobraInstaller."""

    configured = cache_dir or os.environ.get(COBRA_INSTALLER_CACHE_DIR_ENV)
    if configured:
        return Path(configured).expanduser()
    hub_dir = Path(hub_cache_dir).expanduser() if hub_cache_dir else package_cache_dir()
    return hub_dir / _INSTALLER_CACHE_SUBDIR
