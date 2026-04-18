"""Façade interna para acceso a inventario/estado legacy.

Regla arquitectónica: rutas públicas no deben importar directamente módulos
legacy del dominio principal; usar este namespace `internal_compat`.
"""

from __future__ import annotations

from pcobra.cobra.architecture.backend_policy import (
    INTERNAL_BACKENDS,
    INTERNAL_COMPATIBILITY_RETIREMENT_WINDOW,
)
from pcobra.cobra.architecture.legacy_backend_lifecycle import (
    lifecycle_status_for_backend,
    legacy_backend_warning_message,
)

__all__ = [
    "INTERNAL_BACKENDS",
    "INTERNAL_COMPATIBILITY_RETIREMENT_WINDOW",
    "lifecycle_status_for_backend",
    "legacy_backend_warning_message",
]
