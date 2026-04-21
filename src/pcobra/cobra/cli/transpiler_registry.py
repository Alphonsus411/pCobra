"""Helpers CLI para consumir el registro canónico de transpiladores."""

from __future__ import annotations

from types import MappingProxyType
from typing import Mapping

from pcobra.cobra.transpilers.registry import (
    ensure_entrypoint_transpilers_loaded_once,
    get_transpilers,
    official_transpiler_targets,
)


def cli_transpilers() -> Mapping[str, type]:
    """Devuelve un snapshot inmutable del registro consolidado para capa CLI."""
    ensure_entrypoint_transpilers_loaded_once()
    return MappingProxyType(get_transpilers(include_plugins=True))


def cli_transpiler_targets() -> tuple[str, ...]:
    """Devuelve los targets públicos canónicos para ``choices`` en CLI."""
    return official_transpiler_targets()
