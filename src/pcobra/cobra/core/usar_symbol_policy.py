"""Shim canónico bajo pcobra.cobra.core para política de símbolos `usar`."""

from importlib import import_module as _import_module

from pcobra.core.usar_symbol_policy import (
    build_and_validate_usar_symbol_metadata,
    depuracion_saneamiento_usar_habilitada,
    sanear_exportables_para_usar,
)

_policy = _import_module("pcobra.core.usar_symbol_policy")

for _name in dir(_policy):
    if not _name.startswith("_"):
        globals()[_name] = getattr(_policy, _name)

__all__ = [name for name in globals() if not name.startswith("_")]
