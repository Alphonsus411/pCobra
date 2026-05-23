"""Adaptador canónico de configuración Cobra."""

from ...core.cobra_config import *  # noqa: F403
from ...core import cobra_config as _cobra_config

__all__ = [name for name in dir(_cobra_config) if not name.startswith("_")]
