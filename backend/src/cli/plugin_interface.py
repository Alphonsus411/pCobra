"""M\xf3dulo interno deprecado.

Este archivo se mantiene por compatibilidad pero las clases y funciones
relacionadas con plugins se encuentran ahora en ``src.cli.plugin``.
"""

from .plugin import PluginInterface

__all__ = ["PluginInterface"]
