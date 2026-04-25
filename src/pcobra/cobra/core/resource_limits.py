"""Adaptador canónico de límites de recursos."""

from ...core.resource_limits import *  # noqa: F403
from ...core import resource_limits as _resource_limits

__all__ = [name for name in dir(_resource_limits) if not name.startswith("_")]
