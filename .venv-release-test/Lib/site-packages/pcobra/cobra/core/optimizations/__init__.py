"""Adaptador canónico de optimizaciones."""

from ....core.optimizations import *  # noqa: F403
from ....core import optimizations as _optimizations

__all__ = [name for name in dir(_optimizations) if not name.startswith("_")]
