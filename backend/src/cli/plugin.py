"""Utilidades para la carga y registro de plugins de la CLI.

Este m\xf3dulo combina las clases y funciones que antes estaban en
``plugin_interface`` y ``plugin_loader``. Se mantiene aqu\xed para unificar la
API p\fablica relacionada con plugins.
"""

import logging
from abc import ABC, abstractmethod
from importlib import import_module
from importlib.metadata import entry_points

from .commands.base import BaseCommand
from .plugin_registry import registrar_plugin, obtener_registro


class PluginInterface(ABC):
    """Interfaz base para plugins de la CLI."""

    #: Nombre del plugin o subcomando
    name: str = ""

    #: Versi\xf3n del plugin
    version: str = "0.1"

    #: Autor del plugin
    author: str = ""

    #: Breve descripci\xf3n del plugin
    description: str = ""

    @abstractmethod
    def register_subparser(self, subparsers):
        """Registra los argumentos del subcomando en el parser."""
        raise NotImplementedError

    @abstractmethod
    def run(self, args):
        """Ejecuta la l\xf3gica del plugin."""
        raise NotImplementedError


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
    except ValueError:
        logging.error(f"Ruta de plugin inv\xe1lida: {ruta}")
        return None

    try:
        module = import_module(module_name)
    except Exception as exc:
        logging.error(f"Error importando m\xf3dulo {module_name}: {exc}")
        return None

    try:
        plugin_cls = getattr(module, class_name)
    except AttributeError:
        logging.error(f"No se encontr\xf3 la clase {class_name} en {module_name}")
        return None

    if not issubclass(plugin_cls, PluginInterface):
        logging.warning(
            f"El plugin {ruta} no implementa PluginInterface"
        )
        return None

    try:
        instancia = plugin_cls()
    except Exception as exc:
        logging.error(f"Error instanciando plugin {ruta}: {exc}")
        return None

    if not getattr(instancia, "name", ""):
        logging.warning(f"Plugin {ruta} no define atributo name")
        return None

    version = getattr(instancia, "version", "0")
    registrar_plugin(instancia.name, version)
    return instancia


__all__ = [
    "PluginInterface",
    "PluginCommand",
    "descubrir_plugins",
    "cargar_plugin_seguro",
    "registrar_plugin",
    "obtener_registro",
]
