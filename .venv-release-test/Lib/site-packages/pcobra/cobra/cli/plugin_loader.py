"""Módulo interno deprecado.
Las utilidades de carga y las clases para plugins ahora residen en
``cobra.cli.plugin``.

Este módulo será eliminado en la versión 2.0.0.
"""
import warnings
from typing import Optional, List

try:
    from pcobra.cobra.cli.plugin import PluginCommand, cargar_plugin_seguro, descubrir_plugins
    
    warnings.warn(
        "El módulo plugin_loader está deprecado. Use cobra.cli.plugin en su lugar.",
        DeprecationWarning,
        stacklevel=2
    )
    
    __all__ = [
        "PluginCommand",
        "descubrir_plugins",
        "cargar_plugin_seguro",
    ]
    
except ImportError as e:
    raise ImportError(
        "No se pudo importar cobra.cli.plugin. "
        "Asegúrese de tener instalada la versión correcta del paquete."
    ) from e