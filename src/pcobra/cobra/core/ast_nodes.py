"""Reexporta los nodos del módulo ``core.ast_nodes`` para el paquete ``cobra``."""

from pcobra.core import ast_nodes as _ast_nodes

# Reexportar todos los símbolos públicos definidos en ``core.ast_nodes``.
__all__ = [name for name in dir(_ast_nodes) if not name.startswith("_")]
globals().update({name: getattr(_ast_nodes, name) for name in __all__})

