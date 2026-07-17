"""Proveedores de índices y artefactos para paquetes Cobra."""

from pcobra.cobra.hub.providers.github import GitHubReleaseProvider
from pcobra.cobra.hub.providers.http import HttpCobraHubRepository
from pcobra.cobra.hub.providers.pypi import PyPIProvider
from pcobra.cobra.hub.providers.local import LocalArtifactProvider

__all__ = [
    "GitHubReleaseProvider",
    "HttpCobraHubRepository",
    "LocalArtifactProvider",
    "PyPIProvider",
]
