"""Shim de compatibilidad para imports generados de nativos."""

from importlib import import_module as _import_module

_nativos = _import_module("pcobra.core.nativos")
for _name in getattr(_nativos, "__all__", ()):  # pragma: no branch
    globals()[_name] = getattr(_nativos, _name)

__all__ = list(getattr(_nativos, "__all__", ()))
