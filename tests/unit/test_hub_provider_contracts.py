"""Compatibilidad de los contratos de proveedores de CobraHub."""

from __future__ import annotations

import inspect
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from pcobra.cobra.cli.cobrahub_client import CobraHubClient
from pcobra.cobra.cli.cobrahub_packages import CobraHubPackages
from pcobra.cobra.hub import (
    ArtifactProvider,
    GitHubReleaseProvider,
    PackageIndex,
    PackageProviderError,
    PackageRepository,
    PyPIProvider,
)
from pcobra.cobra.hub.providers.http import HttpCobraHubRepository
from pcobra.cobra.hub.repository import DownloadedPackage


def test_package_repository_conserva_superficie_legacy() -> None:
    assert {
        "publish",
        "search",
        "download",
        "read_metadata",
    } <= PackageRepository.__dict__.keys()
    assert list(inspect.signature(PackageRepository.download).parameters) == [
        "self",
        "name",
        "version",
    ]


def test_nuevos_protocolos_separan_indice_y_artefactos() -> None:
    assert {"search", "list_versions", "get_metadata"} <= PackageIndex.__dict__.keys()
    assert {"acquire", "verify"} <= ArtifactProvider.__dict__.keys()


def test_http_es_implementacion_canonica_y_reexport_compatible() -> None:
    from pcobra.cobra.hub.repository import HttpCobraHubRepository as LegacyImport

    assert LegacyImport is HttpCobraHubRepository
    for method in (
        "publish",
        "search",
        "download",
        "read_metadata",
        "list_versions",
        "get_metadata",
        "acquire",
        "verify",
    ):
        assert callable(getattr(HttpCobraHubRepository, method))


def test_http_acquire_delega_en_download_sin_cambiar_firma() -> None:
    repository = HttpCobraHubRepository(MagicMock())
    downloaded = DownloadedPackage(Path("demo.co"), "demo", "1.0.0", "abc")
    repository.download = MagicMock(return_value=downloaded)  # type: ignore[method-assign]

    assert repository.acquire("demo", "1.0.0") is downloaded
    repository.download.assert_called_once_with("demo", "1.0.0")


@pytest.mark.parametrize("provider_type", [PyPIProvider, GitHubReleaseProvider])
@pytest.mark.parametrize(
    ("method", "args"),
    [
        ("search", ("demo",)),
        ("list_versions", ("demo",)),
        ("get_metadata", ("demo",)),
        ("acquire", ("demo",)),
        ("verify", (DownloadedPackage(Path("demo.co"), "demo"),)),
        ("publish", (Path("demo.co"), {}, "abc")),
    ],
)
def test_proveedores_experimentales_fallan_de_forma_controlada(
    provider_type: type, method: str, args: tuple[object, ...]
) -> None:
    with pytest.raises(PackageProviderError, match="aún no está soportada"):
        getattr(provider_type(), method)(*args)


def test_cliente_y_fachada_conservan_metodos_y_repositorio_inyectable() -> None:
    assert {"publicar_paquete", "buscar_paquetes", "instalar_paquete"} <= (
        CobraHubClient.__dict__.keys()
    )
    client = MagicMock(spec=CobraHubClient)
    repository = MagicMock(spec=PackageRepository)

    packages = CobraHubPackages(client, repository)

    assert packages.client is client
    assert packages.repository is repository
