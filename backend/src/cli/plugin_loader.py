import logging
from importlib.metadata import entry_points

from .commands.base import BaseCommand
from .plugin_interface import PluginInterface


class PluginCommand(BaseCommand, PluginInterface):
    """Clase base para implementar comandos externos mediante plugins."""


def descubrir_plugins():
    """Descubre e instancia los plugins registrados bajo ``cobra.plugins``."""
    plugins = []
    try:
        eps = entry_points(group="cobra.plugins")
    except TypeError:  # Compatibilidad con versiones antiguas
        eps = entry_points().get("cobra.plugins", [])

    for ep in eps:
        try:
            plugin_cls = ep.load()
            if not issubclass(plugin_cls, PluginInterface):
                logging.warning(
                    f"El plugin {ep.name} no implementa PluginInterface"
                )
                continue
            plugins.append(plugin_cls())
        except Exception as exc:
            logging.error(f"Error cargando plugin {ep.name}: {exc}")
    return plugins
