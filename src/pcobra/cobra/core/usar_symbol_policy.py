"""Shim canónico bajo pcobra.cobra.core para política de símbolos `usar`."""

from importlib import import_module as _import_module

_policy = _import_module("pcobra.core.usar_symbol_policy")
for _name in dir(_policy):
    if not _name.startswith("_"):
        globals()[_name] = getattr(_policy, _name)

__all__ = [name for name in globals() if not name.startswith("_")]
