"""Adaptador compatible del resolvedor de instalación CobraHub."""

from pcobra.cobra.hub.errors import CobraHubError
from pcobra.cobra.hub.installation import CobraHubResolver as _HubResolver
from pcobra.cobra.hub.models import CobraHubResolution
from pcobra.cobra_installer.project import CobraInstallerError


class CobraHubResolver(_HubResolver):
    """Mantiene la excepción pública esperada por consumidores del Installer."""

    def resolve(
        self,
        name: str,
        version: str,
        *,
        expected_sha256: str | None = None,
        source: str | None = None,
        platform: str = "any",
        architecture: str = "any",
    ) -> CobraHubResolution:
        try:
            return super().resolve(
                name,
                version,
                expected_sha256=expected_sha256,
                source=source,
                platform=platform,
                architecture=architecture,
            )
        except CobraHubError as exc:
            raise CobraInstallerError(str(exc)) from exc


__all__ = ["CobraInstallerError", "CobraHubResolution", "CobraHubResolver"]
