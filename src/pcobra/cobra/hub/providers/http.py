"""Proveedor HTTP canónico para CobraHub."""

from __future__ import annotations

import hashlib
import os
import shutil
import urllib.parse
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
from pcobra.cobra.hub.repository import (
    DownloadedPackage,
    _cache_filename,
    _normalizar_metadatos_paquete,
    _normalizar_resultado_paquete,
    _version_from_response,
    json_dumps,
    package_cache_dir,
)
from pcobra.cobra.hub.transport import CobraHubTransport
from pcobra.cobra.packaging import (
    PackageSearchResult,
    normalizar_nombre_paquete,
    validar_version_paquete,
)


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
            with (
                ruta.open("rb") as f,
                self.client.session.post(
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
                ) as response,
            ):
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
                    status = getattr(
                        getattr(exc, "response", None), "status_code", None
                    )
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

    def list_versions(self, name: str) -> list[str]:
        """Lista las versiones publicadas de un paquete."""
        metadata = self._get_package_resource(name, "versions")
        values = (
            metadata.get("versions", []) if isinstance(metadata, dict) else metadata
        )
        try:
            return [validar_version_paquete(str(value)) for value in values]
        except (TypeError, ValueError) as exc:
            raise PackageResolutionError(str(exc)) from exc

    def get_metadata(self, name: str, version: str | None = None) -> dict[str, Any]:
        """Obtiene metadatos remotos para un paquete y versión opcional."""
        metadata = self._get_package_resource(name, "metadata", version)
        if not isinstance(metadata, dict):
            raise PackageResolutionError("Los metadatos remotos no son un objeto")
        return metadata

    def acquire(self, name: str, version: str | None = None) -> DownloadedPackage:
        """Adquiere un artefacto conservando ``download`` como alias histórico."""
        return self.download(name, version)

    def verify(self, artifact: DownloadedPackage) -> bool:
        """Verifica que el artefacto exista y coincida con su checksum SHA-256."""
        if not artifact.path.is_file():
            raise PackageIntegrityError(f"No existe el artefacto: {artifact.path}")
        if artifact.checksum is None:
            raise PackageIntegrityError("El artefacto no incluye checksum")
        digest = hashlib.sha256(artifact.path.read_bytes()).hexdigest()
        if digest != artifact.checksum:
            raise PackageIntegrityError("Verificación de integridad fallida")
        return True

    def _get_package_resource(
        self, name: str, resource: str, version: str | None = None
    ) -> Any:
        try:
            normalized_name = normalizar_nombre_paquete(name)
            normalized_version = (
                validar_version_paquete(version) if version is not None else None
            )
            with self.client.session.get(
                f"{self.client.base_url}/paquetes/"
                f"{urllib.parse.quote(normalized_name)}/{resource}",
                **(
                    {"params": {"version": normalized_version}}
                    if normalized_version
                    else {}
                ),
                timeout=(self.client.CONNECT_TIMEOUT, self.client.READ_TIMEOUT),
            ) as response:
                response.raise_for_status()
                data = response.json()
            if not isinstance(data, (dict, list)):
                raise PackageResolutionError("Respuesta de índice no válida")
            return data
        except CobraHubError:
            raise
        except (TypeError, ValueError, KeyError) as exc:
            raise PackageResolutionError(str(exc)) from exc
        except Exception as exc:
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


__all__ = ["HttpCobraHubRepository"]
