"""Façade interna para acceso a module_map desde capas públicas de imports/CLI."""

from __future__ import annotations

from typing import Any

from pcobra.cobra.transpilers.module_map import (
    MODULE_MAP_PATH,
    get_toml_map as _get_toml_map,
    resolve_backend_for_module as _resolve_backend_for_module,
)


def get_toml_map() -> dict[str, Any]:
    """Retorna el mapa TOML canónico de módulos."""
    return _get_toml_map()


def resolve_backend_for_module(module: str, backend: str) -> str | None:
    """Resuelve backend mapeado para un módulo."""
    return _resolve_backend_for_module(module, backend)


__all__ = ["MODULE_MAP_PATH", "get_toml_map", "resolve_backend_for_module"]

