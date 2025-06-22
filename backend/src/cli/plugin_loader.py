import logging
from importlib.metadata import entry_points

from .commands.base import BaseCommand


class PluginCommand(BaseCommand):
    """Clase base para comandos de plugins."""
    pass


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
            if not issubclass(plugin_cls, PluginCommand):
                logging.warning(f"El plugin {ep.name} no es PluginCommand")
                continue
            plugins.append(plugin_cls())
        except Exception as exc:
            logging.error(f"Error cargando plugin {ep.name}: {exc}")
    return plugins
