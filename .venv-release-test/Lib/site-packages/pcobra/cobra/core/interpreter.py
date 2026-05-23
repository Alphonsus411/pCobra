"""Adaptador canónico del intérprete Cobra."""

from ...core.interpreter import *  # noqa: F403
from ...core import interpreter as _interpreter

__all__ = [name for name in dir(_interpreter) if not name.startswith("_")]
