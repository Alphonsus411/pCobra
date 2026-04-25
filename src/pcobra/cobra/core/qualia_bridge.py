"""Adaptador canónico de Qualia bridge."""

from ...core.qualia_bridge import *  # noqa: F403
from ...core import qualia_bridge as _qualia_bridge

__all__ = [name for name in dir(_qualia_bridge) if not name.startswith("_")]
