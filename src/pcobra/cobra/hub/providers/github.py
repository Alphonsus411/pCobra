"""Proveedor experimental para artefactos de GitHub Releases."""

from pcobra.cobra.hub.providers._experimental import UnsupportedExperimentalProvider


class GitHubReleaseProvider(UnsupportedExperimentalProvider):
    """Reserva GitHub Releases sin descargar ni publicar artefactos todavía."""

    provider_name = "GitHub Releases"


__all__ = ["GitHubReleaseProvider"]
