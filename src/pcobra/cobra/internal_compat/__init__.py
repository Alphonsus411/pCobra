"""Namespace explícito para compatibilidad interna/legacy.

Este paquete encapsula contratos que no forman parte de la superficie pública
estable y deben consumirse únicamente por rutas de migración interna.
"""

from pcobra.cobra.internal_compat.legacy_contracts import (
    INTERNAL_BACKENDS,
    INTERNAL_COMPATIBILITY_RETIREMENT_WINDOW,
    lifecycle_status_for_backend,
    legacy_backend_warning_message,
)

__all__ = [
    "INTERNAL_BACKENDS",
    "INTERNAL_COMPATIBILITY_RETIREMENT_WINDOW",
    "lifecycle_status_for_backend",
    "legacy_backend_warning_message",
]
