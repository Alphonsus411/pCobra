"""Adaptador canónico de visitor bajo ``pcobra.cobra.core``."""

from ...core.visitor import *  # noqa: F403
from ...core import visitor as _visitor

__all__ = [name for name in dir(_visitor) if not name.startswith("_")]
