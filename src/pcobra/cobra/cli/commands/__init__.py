"""Paquete de comandos CLI.

Mantiene compatibilidad con imports legacy tipo ``import cobra.cli.commands.bench_cmd``
sin importar módulos de comandos concretos durante el arranque canónico de la CLI.
"""

from __future__ import annotations

from importlib import import_module as _import_module
import sys as _sys
from types import ModuleType as _ModuleType

_LEGACY_COMMAND_MODULE_ALIASES = frozenset(
    {
        "bench_cmd",
        "bench_transpilers_cmd",
        "benchmarks_cmd",
        "benchmarks2_cmd",
    }
)


def __getattr__(name: str) -> _ModuleType:
    """Resuelve módulos legacy de benchmark bajo demanda.

    Antes este paquete importaba esos módulos al cargar ``commands.base``. Eso
    hacía que ``CliApplication`` precargara comandos concretos aunque el parser
    todavía no los hubiese registrado.
    """

    if name not in _LEGACY_COMMAND_MODULE_ALIASES:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

    module = _import_module(f"{__name__}.{name}")
    globals()[name] = module
    _sys.modules.setdefault(f"cobra.cli.commands.{name}", module)
    return module


__all__ = sorted(_LEGACY_COMMAND_MODULE_ALIASES)
