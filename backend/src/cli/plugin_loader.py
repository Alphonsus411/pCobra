"""M\xf3dulo interno deprecado.

Las utilidades de carga y las clases para plugins ahora residen en
``src.cli.plugin``.
"""

from .plugin import PluginCommand, descubrir_plugins, cargar_plugin_seguro

__all__ = [
    "PluginCommand",
    "descubrir_plugins",
    "cargar_plugin_seguro",
]
