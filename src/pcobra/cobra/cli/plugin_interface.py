"""Módulo interno deprecado.

Este módulo está deprecado desde la versión 2.0.0.
Las clases y funciones relacionadas con plugins se encuentran ahora en 
``cobra.cli.plugin``. Por favor, actualiza tus imports para usar el nuevo módulo.

Example:
    from pcobra.cobra.cli.plugin import PluginInterface  # Forma recomendada
"""
import warnings

warnings.warn(
    "El módulo plugin_interface está deprecado. "
    "Use cobra.cli.plugin en su lugar.",
    DeprecationWarning,
    stacklevel=2
)

from pcobra.cobra.cli.plugin import PluginInterface

__all__ = ["PluginInterface"]