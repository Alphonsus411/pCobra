"""Contrato CLI para acceso a transpiladores.

ÚNICA FUENTE:
- Esta capa CLI debe consumir exclusivamente ``pcobra.cobra.transpilers.registry``.
- Los comandos CLI no deben declarar catálogos locales de backends/transpiladores.
- Los comandos CLI deben usar ``cli_transpilers()`` y/o ``cli_transpiler_targets()``
  para obtener snapshots canónicos.

Compatibilidad:
- El ciclo de plugins/entrypoints se mantiene a través de
  ``ensure_entrypoint_transpilers_loaded_once()``.
"""

from __future__ import annotations

from typing import Mapping

from pcobra.cobra.transpilers.registry import (
    ensure_entrypoint_transpilers_loaded_once,
    get_transpilers,
    load_entrypoint_transpilers,
    official_transpiler_targets,
    plugin_transpilers,
    register_transpiler_backend,
)
from pcobra.cobra.transpilers.module_map import get_toml_map


def cli_transpilers() -> Mapping[str, type]:
    """Devuelve un snapshot inmutable del registro consolidado para capa CLI."""
    return get_transpilers(include_plugins=True, ensure_entrypoints_loaded=True)


def cli_transpiler_targets() -> tuple[str, ...]:
    """Devuelve los targets públicos canónicos para ``choices`` en CLI."""
    return official_transpiler_targets()


def cli_ensure_entrypoint_transpilers_loaded_once() -> None:
    """Garantiza (idempotente) la carga de transpiladores registrados por entrypoints."""
    ensure_entrypoint_transpilers_loaded_once()


def cli_plugin_transpilers() -> Mapping[str, type]:
    """Devuelve el mapping de transpiladores registrados por plugins."""
    return plugin_transpilers()


def cli_register_transpiler_backend(backend: str, transpiler_cls, *, context: str) -> str:
    """Registra un backend de plugin delegando al registro canónico."""
    return register_transpiler_backend(backend, transpiler_cls, context=context)


def cli_load_entrypoint_transpilers() -> tuple[int, int, int]:
    """Carga explícita de entrypoints, manteniendo contrato legacy de retorno."""
    return load_entrypoint_transpilers()


def cli_toml_map() -> dict:
    """Devuelve el mapa de configuración TOML para consumo compartido en CLI."""
    return get_toml_map()
