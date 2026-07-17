"""Abstracción de repositorios de paquetes Cobra.

Esta capa encapsula la publicación, búsqueda, descarga y lectura de metadatos
sin acoplar esas operaciones al Lexer ni al Parser. En el futuro permitirá
incorporar repositorios indexados, mirrors, autenticación y resolución de
versiones sin tocar las fases de análisis del lenguaje.
"""

from __future__ import annotations

import hashlib
import json
import logging
import os
import shutil
import urllib.parse
from dataclasses import dataclass
from email.message import Message
from pathlib import Path
from typing import Any, Protocol

from pcobra.cobra.hub.errors import (
    CobraHubError,
    PackageCompatibilityError,
    PackageIntegrityError,
    PackageNotFoundError,
    PackageProviderError,
    PackageResolutionError,
)
from pcobra.cobra.hub.transport import CobraHubTransport
from pcobra.cobra.packaging import (
    PackageSearchResult,
    manifest_from_dict,
    manifest_to_dict,
    normalizar_nombre_paquete,
    validar_version_paquete,
)

logger = logging.getLogger(__name__)


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


class HttpCobraHubRepository:
    """Repositorio CobraHub respaldado por HTTP usando un ``CobraHubClient``."""

    def __init__(self, client: CobraHubTransport) -> None:
        self.client = client

    def publish(
        self, package_path: str | Path, metadata: dict[str, Any], checksum: str
    ) -> bool:
        """Publica un paquete .co mediante la API HTTP de CobraHub."""
        ruta = Path(package_path)
        try:
            metadata = _normalizar_metadatos_paquete(metadata)
        except (TypeError, ValueError, KeyError) as exc:
            raise PackageResolutionError(str(exc)) from exc
        try:
            with ruta.open("rb") as f, self.client.session.post(
                f"{self.client.base_url}/paquetes",
                files={"file": f},
                data={"metadata": json_dumps(metadata)},
                headers={
                    "X-Content-Checksum": checksum,
                    "Idempotency-Key": checksum,
                },
                timeout=(
                    self.client.CONNECT_TIMEOUT,
                    self.client.READ_TIMEOUT,
                ),
            ) as response:
                response.raise_for_status()
            cache_path = package_cache_dir() / ruta.name
            if ruta.resolve() != cache_path.resolve():
                shutil.copy2(ruta, cache_path)
        except CobraHubError:
            raise
        except Exception as exc:
            raise PackageProviderError(str(exc)) from exc
        return True

    def search(self, query: str) -> list[PackageSearchResult]:
        """Busca paquetes mediante la API HTTP de CobraHub."""
        try:
            with self.client.session.get(
                f"{self.client.base_url}/paquetes",
                params={"q": query},
                timeout=(self.client.CONNECT_TIMEOUT, self.client.READ_TIMEOUT),
            ) as response:
                response.raise_for_status()
                data = response.json() if hasattr(response, "json") else []
            items = data.get("results", []) if isinstance(data, dict) else data
            return [_normalizar_resultado_paquete(item) for item in list(items)]
        except CobraHubError:
            raise
        except (TypeError, ValueError, KeyError) as exc:
            raise PackageResolutionError(str(exc)) from exc
        except Exception as exc:
            raise PackageProviderError(str(exc)) from exc

    def download(self, name: str, version: str | None = None) -> DownloadedPackage:
        """Descarga un paquete por nombre y versión opcional en la caché local."""
        try:
            normalized_name = normalizar_nombre_paquete(name)
            normalized_version = (
                validar_version_paquete(version) if version is not None else None
            )
        except (TypeError, ValueError) as exc:
            raise PackageResolutionError(str(exc)) from exc
        cache_path = package_cache_dir() / _cache_filename(
            normalized_name, normalized_version
        )
        try:
            with self.client.session.get(
                f"{self.client.base_url}/paquetes/{urllib.parse.quote(normalized_name)}",
                **(
                    {"params": {"version": normalized_version}}
                    if normalized_version
                    else {}
                ),
                timeout=(self.client.CONNECT_TIMEOUT, self.client.READ_TIMEOUT),
                stream=True,
            ) as response:
                try:
                    response.raise_for_status()
                except Exception as exc:
                    status = getattr(getattr(exc, "response", None), "status_code", None)
                    status = status or getattr(response, "status_code", None)
                    if status == 404:
                        raise PackageNotFoundError(str(exc)) from exc
                    raise PackageProviderError(str(exc)) from exc
                checksum_servidor = response.headers.get("X-Content-Checksum")
                version_servidor = _version_from_response(response)
                if version_servidor:
                    try:
                        version_servidor = validar_version_paquete(version_servidor)
                    except (TypeError, ValueError) as exc:
                        raise PackageCompatibilityError(str(exc)) from exc
                if version_servidor and version_servidor != normalized_version:
                    cache_path = package_cache_dir() / _cache_filename(
                        normalized_name, version_servidor
                    )
                sha256 = hashlib.sha256()
                tamaño_total = 0

                with open(cache_path, "wb") as out:
                    for chunk in response.iter_content(
                        chunk_size=self.client.CHUNK_SIZE
                    ):
                        if not chunk:
                            continue
                        tamaño_total += len(chunk)
                        if tamaño_total > self.client.MAX_FILE_SIZE:
                            out.close()
                            os.unlink(cache_path)
                            raise PackageIntegrityError(
                                "Archivo descargado demasiado grande"
                            )
                        sha256.update(chunk)
                        out.write(chunk)

            digest = sha256.hexdigest()
            if checksum_servidor and digest != checksum_servidor:
                os.unlink(cache_path)
                raise PackageIntegrityError("Verificación de integridad fallida")

            return DownloadedPackage(
                path=cache_path,
                name=normalized_name,
                version=version_servidor or normalized_version,
                checksum=checksum_servidor or digest,
            )
        except CobraHubError:
            if cache_path.exists():
                os.unlink(cache_path)
            raise
        except Exception as exc:
            if cache_path.exists():
                os.unlink(cache_path)
            raise PackageProviderError(str(exc)) from exc

    def read_metadata(self, package_path: str | Path) -> dict[str, Any]:
        """Lee metadatos de un paquete local usando el validador de paquetes Cobra."""
        from pcobra.cobra.packaging import es_paquete_cobra, validar_paquete

        if not es_paquete_cobra(package_path):
            raise PackageIntegrityError(
                "No es un paquete Cobra: debe ser ZIP y contener cobra.pkg.json"
            )
        try:
            info = validar_paquete(package_path)
            return _normalizar_metadatos_paquete(info.manifest)
        except CobraHubError:
            raise
        except Exception as exc:
            raise PackageIntegrityError(str(exc)) from exc


def _normalizar_metadatos_paquete(metadata: dict[str, Any]) -> dict[str, Any]:
    """Devuelve metadatos canónicos preservando campos opcionales soportados."""
    return manifest_to_dict(manifest_from_dict(dict(metadata)))


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


__all__ = [
    "DownloadedPackage",
    "HttpCobraHubRepository",
    "PackageRepository",
    "install_dir",
    "json_dumps",
    "package_cache_dir",
]
