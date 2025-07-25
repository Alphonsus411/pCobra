"""M\xf3dulo interno deprecado.

Las utilidades de carga y las clases para plugins ahora residen en
``src.cli.plugin``.
"""

from src.cli.plugin import PluginCommand, cargar_plugin_seguro, descubrir_plugins

__all__ = [
    "PluginCommand",
    "descubrir_plugins",
    "cargar_plugin_seguro",
]
