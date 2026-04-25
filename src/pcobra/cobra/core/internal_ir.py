"""Adaptador canónico de IR interno."""

from ...core.internal_ir import *  # noqa: F403
from ...core import internal_ir as _internal_ir

__all__ = [name for name in dir(_internal_ir) if not name.startswith("_")]
