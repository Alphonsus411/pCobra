"""Abstracción de repositorios de paquetes Cobra.

Esta capa encapsula la publicación, búsqueda, descarga y lectura de metadatos
sin acoplar esas operaciones al Lexer ni al Parser. En el futuro permitirá
incorporar repositorios indexados, mirrors, autenticación y resolución de
versiones sin tocar las fases de análisis del lenguaje.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from email.message import Message
from pathlib import Path
from typing import Any, Protocol, cast

from pcobra.cobra.packaging import (
    PackageSearchResult,
    manifest_from_dict,
    manifest_to_dict,
)


@dataclass(frozen=True)
class DownloadedPackage:
    """Resultado de una descarga de paquete desde un repositorio."""

    path: Path
    name: str
    version: str | None = None
    checksum: str | None = None


class PackageRepository(Protocol):
    """Contrato independiente para repositorios de paquetes Cobra."""

    def publish(
        self, package_path: str | Path, metadata: dict[str, Any], checksum: str
    ) -> bool:
        """Publica un paquete ya validado con sus metadatos y checksum."""
        ...

    def search(self, query: str) -> list[PackageSearchResult]:
        """Busca paquetes por consulta textual."""
        ...

    def download(self, name: str, version: str | None = None) -> DownloadedPackage:
        """Descarga un paquete y devuelve su ubicación local/cacheada."""
        ...

    def read_metadata(self, package_path: str | Path) -> dict[str, Any]:
        """Lee los metadatos de un paquete local."""
        ...


class PackageIndex(Protocol):
    """Contrato de consulta de un índice de paquetes, sin adquirir artefactos."""

    def search(self, query: str) -> list[PackageSearchResult]: ...

    def list_versions(self, name: str) -> list[str]: ...

    def get_metadata(self, name: str, version: str | None = None) -> dict[str, Any]: ...


class ArtifactProvider(Protocol):
    """Contrato para adquirir y verificar artefactos de paquetes."""

    def acquire(self, name: str, version: str | None = None) -> DownloadedPackage: ...

    def verify(self, artifact: DownloadedPackage) -> bool: ...


def _normalizar_metadatos_paquete(metadata: dict[str, Any]) -> dict[str, Any]:
    """Devuelve metadatos canónicos preservando campos opcionales soportados."""
    return cast(dict[str, Any], manifest_to_dict(manifest_from_dict(dict(metadata))))


def _normalizar_lista_str(value: Any) -> list[str] | None:
    if value is None:
        return None
    if isinstance(value, list):
        return [str(item) for item in value]
    return [str(value)]


def _normalizar_dependencias(value: Any) -> dict[str, str] | None:
    if value is None:
        return None
    if not isinstance(value, dict):
        return None
    return {str(name): str(version) for name, version in value.items()}


def _normalizar_resultado_paquete(item: Any) -> PackageSearchResult:
    """Convierte respuestas variadas del servidor al modelo mínimo público."""
    if not isinstance(item, dict):
        item = {"name": str(item)}

    name = item.get("name") or item.get("nombre") or item.get("package")
    if not name:
        name = Path(
            str(item.get("filename") or item.get("archivo") or "paquete.co")
        ).stem

    return PackageSearchResult(
        name=str(name),
        version=_optional_str(item.get("version")),
        filename=_optional_str(item.get("filename") or item.get("archivo")),
        checksum=_optional_str(
            item.get("checksum")
            or item.get("sha256")
            or item.get("digest")
            or item.get("content_checksum")
        ),
        download_url=_optional_str(
            item.get("download_url") or item.get("url") or item.get("href")
        ),
        remote_id=_optional_str(item.get("remote_id") or item.get("id")),
        description=_optional_str(item.get("description") or item.get("descripcion")),
        authors=_normalizar_lista_str(
            item["authors"] if "authors" in item else item.get("autores")
        ),
        license=_optional_str(item.get("license") or item.get("licencia")),
        homepage=_optional_str(
            item.get("homepage") or item.get("home_page") or item.get("project_url")
        ),
        dependencies=_normalizar_dependencias(
            item["dependencies"] if "dependencies" in item else item.get("dependencias")
        ),
    )


def _optional_str(value: Any) -> str | None:
    if value is None:
        return None
    value = str(value)
    return value or None


def _cache_filename(nombre: str, version: str | None) -> str:
    return f"{nombre}-{version}.co" if version else f"{nombre}.co"


def _version_from_response(response: Any) -> str | None:
    headers = getattr(response, "headers", {}) or {}
    version = headers.get("X-Package-Version") or headers.get("X-Cobra-Package-Version")
    if version:
        return str(version)
    content_disposition = headers.get("Content-Disposition")
    if not content_disposition:
        return None
    msg = Message()
    msg["Content-Disposition"] = content_disposition
    filename = msg.get_filename()
    if not filename:
        return None
    stem = Path(filename).stem
    if "-" not in stem:
        return None
    return stem.rsplit("-", 1)[1] or None


def package_cache_dir() -> Path:
    """Devuelve el directorio de caché local para paquetes CobraHub."""
    cache = Path(
        os.environ.get(
            "COBRAHUB_CACHE_DIR", str(Path.home() / ".cobra" / "hub" / "cache")
        )
    ).expanduser()
    cache.mkdir(parents=True, exist_ok=True)
    return cache


def install_dir() -> Path:
    """Devuelve el directorio de instalación por defecto para paquetes."""
    dest = Path(
        os.environ.get("COBRAHUB_INSTALL_DIR", str(Path.home() / ".cobra" / "packages"))
    ).expanduser()
    dest.mkdir(parents=True, exist_ok=True)
    return dest


def json_dumps(value: Any) -> str:
    """Serializa metadatos de paquete de forma estable."""
    return json.dumps(value, ensure_ascii=False, sort_keys=True)


from pcobra.cobra.hub.providers.http import HttpCobraHubRepository

__all__ = [
    "ArtifactProvider",
    "DownloadedPackage",
    "HttpCobraHubRepository",
    "PackageIndex",
    "PackageRepository",
    "install_dir",
    "json_dumps",
    "package_cache_dir",
]
