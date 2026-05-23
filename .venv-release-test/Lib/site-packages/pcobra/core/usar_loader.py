"""Compat wrapper para `usar_loader` en `pcobra.core`.

Este módulo delega en `pcobra.cobra.usar_loader` para mantener una sola
fuente de verdad de la política canónica de resolución de `usar`.
"""

from __future__ import annotations

from pcobra.cobra import usar_loader as _impl

__all__ = list(getattr(_impl, "__all__", []))


def __getattr__(name: str):
    return getattr(_impl, name)


def __dir__() -> list[str]:
    return sorted(set(globals()) | set(dir(_impl)))


def obtener_modulo(*args, **kwargs):
    """Delega en la implementación canónica de `pcobra.cobra.usar_loader`."""

    return _impl.obtener_modulo(*args, **kwargs)


def obtener_modulo_cobra_oficial(*args, **kwargs):
    """Delega en la implementación canónica de `pcobra.cobra.usar_loader`."""

    return _impl.obtener_modulo_cobra_oficial(*args, **kwargs)


def validar_nombre_modulo_usar(*args, **kwargs):
    """Delega en la implementación canónica de `pcobra.cobra.usar_loader`."""

    return _impl.validar_nombre_modulo_usar(*args, **kwargs)


def sanitizar_exports_publicos(*args, **kwargs):
    """Delega en la implementación canónica de `pcobra.cobra.usar_loader`."""

    return _impl.sanitizar_exports_publicos(*args, **kwargs)
