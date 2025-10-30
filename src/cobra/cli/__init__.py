"""Alias ligero para :mod:`pcobra.cobra.cli`."""

from importlib import import_module
import sys as _sys

_target = import_module("pcobra.cobra.cli")
_sys.modules.setdefault("pcobra.cobra.cli", _target)
_sys.modules.setdefault(__name__, _target)
__all__ = getattr(_target, "__all__", [])
for _name in __all__:
    globals()[_name] = getattr(_target, _name)
