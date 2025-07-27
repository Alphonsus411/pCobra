"""M\xf3dulo interno deprecado.

Este archivo se mantiene por compatibilidad pero las clases y funciones
relacionadas con plugins se encuentran ahora en ``cobra.cli.plugin``.
"""

from cobra.cli.plugin import PluginInterface

__all__ = ["PluginInterface"]
