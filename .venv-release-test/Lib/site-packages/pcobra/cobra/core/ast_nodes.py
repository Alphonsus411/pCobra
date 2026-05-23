"""Adaptador canónico de nodos AST bajo ``pcobra.cobra.core``."""

from ...core import ast_nodes as _ast_nodes

__all__ = [name for name in dir(_ast_nodes) if not name.startswith("_")]
globals().update({name: getattr(_ast_nodes, name) for name in __all__})
