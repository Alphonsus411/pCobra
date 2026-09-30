"""Adaptador canónico de caché AST."""

from ...core.ast_cache import *  # noqa: F403
from ...core import ast_cache as _ast_cache

# Compatibilidad interna para el modo incremental del Parser. Los nombres
# privados no se reexportan mediante ``import *``.
_obtener_ast_sintactico_fragmento = (
    _ast_cache._obtener_ast_sintactico_fragmento
)

__all__ = [name for name in dir(_ast_cache) if not name.startswith("_")]
