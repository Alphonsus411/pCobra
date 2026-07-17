"""Proveedor experimental para índices compatibles con PyPI."""

from pcobra.cobra.hub.providers._experimental import UnsupportedExperimentalProvider


class PyPIProvider(UnsupportedExperimentalProvider):
    """Reserva la integración con PyPI sin instalar ni publicar paquetes."""

    provider_name = "PyPI"


__all__ = ["PyPIProvider"]
