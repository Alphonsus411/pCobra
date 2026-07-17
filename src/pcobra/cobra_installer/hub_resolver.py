"""Adaptador compatible del resolvedor de instalación CobraHub."""

from pcobra.cobra.hub.installation import CobraHubResolver, CobraInstallerError
from pcobra.cobra.hub.models import CobraHubResolution

__all__ = ["CobraInstallerError", "CobraHubResolution", "CobraHubResolver"]
