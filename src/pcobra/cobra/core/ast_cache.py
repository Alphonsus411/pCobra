"""Adaptador canónico de caché AST."""

from ...core.ast_cache import *  # noqa: F403
from ...core import ast_cache as _ast_cache

__all__ = [name for name in dir(_ast_cache) if not name.startswith("_")]
