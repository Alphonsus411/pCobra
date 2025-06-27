import logging
from importlib import import_module
from importlib.metadata import entry_points

from .commands.base import BaseCommand
from .plugin_interface import PluginInterface
from .plugin_registry import registrar_plugin


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
        instancia = cargar_plugin_seguro(ep.value)
        if instancia is not None:
            plugins.append(instancia)
    return plugins


def cargar_plugin_seguro(ruta: str):
    """Carga de forma segura un plugin a partir de ``modulo:Clase``."""
    try:
        module_name, class_name = ruta.split(":", 1)
        module = import_module(module_name)
        plugin_cls = getattr(module, class_name)
        if not issubclass(plugin_cls, PluginInterface):
            logging.warning(
                f"El plugin {ruta} no implementa PluginInterface"
            )
            return None
        instancia = plugin_cls()
        registrar_plugin(instancia.name, getattr(instancia, "version", "0"))
        return instancia
    except Exception as exc:
        logging.error(f"Error cargando plugin {ruta}: {exc}")
        return None
