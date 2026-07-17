"""Base segura para proveedores cuyo soporte todavía es experimental."""

from __future__ import annotations

from pathlib import Path
from typing import Any, NoReturn

from pcobra.cobra.hub.errors import PackageProviderError
from pcobra.cobra.hub.repository import DownloadedPackage
from pcobra.cobra.packaging import PackageSearchResult


class UnsupportedExperimentalProvider:
    """Rechaza de forma controlada toda operación aún no implementada."""

    provider_name = "experimental"

    def _unsupported(self, operation: str) -> NoReturn:
        raise PackageProviderError(
            f"{self.provider_name}: la operación {operation!r} aún no está soportada"
        )

    def search(self, query: str) -> list[PackageSearchResult]:
        self._unsupported("search")

    def list_versions(self, name: str) -> list[str]:
        self._unsupported("list_versions")

    def get_metadata(self, name: str, version: str | None = None) -> dict[str, Any]:
        self._unsupported("get_metadata")

    def acquire(self, name: str, version: str | None = None) -> DownloadedPackage:
        self._unsupported("acquire")

    def verify(self, artifact: DownloadedPackage) -> bool:
        self._unsupported("verify")

    # Superficie legacy disponible para composición sin ejecutar herramientas externas.
    def publish(
        self, package_path: str | Path, metadata: dict[str, Any], checksum: str
    ) -> bool:
        self._unsupported("publish")

    def download(self, name: str, version: str | None = None) -> DownloadedPackage:
        self._unsupported("download")

    def read_metadata(self, package_path: str | Path) -> dict[str, Any]:
        self._unsupported("read_metadata")
