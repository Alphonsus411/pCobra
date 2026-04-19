"""Helpers CLI para consumir el registro canónico de transpiladores."""

from __future__ import annotations

from functools import lru_cache
from types import MappingProxyType
from typing import Mapping

from pcobra.cobra.transpilers.registry import get_transpilers, official_transpiler_targets


@lru_cache(maxsize=1)
def cli_transpilers() -> Mapping[str, type]:
    """Devuelve un snapshot inmutable del registro canónico para capa CLI."""
    return MappingProxyType(get_transpilers())


def cli_transpiler_targets() -> tuple[str, ...]:
    """Devuelve los targets públicos canónicos para ``choices`` en CLI."""
    return official_transpiler_targets()
