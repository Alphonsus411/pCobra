"""Composición predeterminada de las dependencias remotas de CobraHub."""

from pcobra.cobra.cli.cobrahub_client import CobraHubClient
from pcobra.cobra.cli.services.cobrahub_service import CobraHubService
from pcobra.cobra.hub.repository import HttpCobraHubRepository


def crear_servicio_cobrahub() -> CobraHubService:
    """Crea el servicio remoto con un cliente y repositorio HTTP compartidos."""
    provider = CobraHubClient()
    repository = HttpCobraHubRepository(provider)
    return CobraHubService(provider=provider, repository=repository)


__all__ = ["crear_servicio_cobrahub"]
