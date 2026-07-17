"""Adaptador compatible del resolvedor de instalación CobraHub."""

from pcobra.cobra.hub.errors import CobraHubError
from pcobra.cobra.hub.installation import CobraHubResolver as _HubResolver
from pcobra.cobra.hub.models import CobraHubResolution
from pcobra.cobra_installer.project import CobraInstallerError


class CobraHubResolver(_HubResolver):
    """Mantiene la excepción pública esperada por consumidores del Installer."""

    def resolve(self, *args, **kwargs):
        try:
            return super().resolve(*args, **kwargs)
        except CobraHubError as exc:
            raise CobraInstallerError(str(exc)) from exc

__all__ = ["CobraInstallerError", "CobraHubResolution", "CobraHubResolver"]
