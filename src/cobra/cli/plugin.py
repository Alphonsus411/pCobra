"""Utilidades para la carga y registro de plugins de la CLI.

Este módulo combina las clases y funciones que antes estaban en
``plugin_interface`` y ``plugin_loader``. Se mantiene aquí para unificar la
API pública relacionada con plugins.
"""

import logging
from abc import ABC, abstractmethod
from importlib import import_module
from importlib.metadata import entry_points
from typing import List, Optional, Any
from argparse import _SubParsersAction

from cobra.cli.commands.base import BaseCommand
from cobra.cli.plugin_registry import (
    obtener_registro,
    obtener_registro_detallado,
    registrar_plugin,
)

# Constantes
DEFAULT_VERSION = "0.1"
DEFAULT_DESCRIPTION = ""
PLUGIN_GROUP = "cobra.plugins"


class PluginInterface(ABC):
    """Interfaz base para plugins de la CLI.
    
    Attributes:
        name: Nombre del plugin o subcomando
        version: Versión del plugin
        author: Autor del plugin
        description: Breve descripción del plugin
    """

    name: str = ""
    version: str = DEFAULT_VERSION
    author: str = ""
    description: str = DEFAULT_DESCRIPTION

    @abstractmethod
    def register_subparser(self, subparsers: _SubParsersAction) -> None:
        """Registra los argumentos del subcomando en el parser.
        
        Args:
            subparsers: Objeto para registrar subcomandos
        """
        raise NotImplementedError

    @abstractmethod
    def run(self, args: Any) -> int:
        """Ejecuta la lógica del plugin.
        
        Args:
            args: Argumentos parseados del comando
            
        Returns:
            int: Código de salida (0 para éxito)
        """
        raise NotImplementedError


class PluginCommand(BaseCommand, PluginInterface):
    """Clase base para implementar comandos externos mediante plugins."""

    def register_subparser(self, subparsers: _SubParsersAction) -> None:
        """Implementación por defecto del registro de subparser."""
        super().register_subparser(subparsers)

    def run(self, args: Any) -> int:
        """Implementación por defecto de la ejecución del comando."""
        return super().run(args)


def descubrir_plugins() -> List[PluginInterface]:
    """Descubre e instancia los plugins registrados bajo ``cobra.plugins``.
    
    Returns:
        List[PluginInterface]: Lista de instancias de plugins cargados correctamente
        
    Raises:
        ImportError: Si hay problemas al cargar los entry points
    """
    plugins: List[PluginInterface] = []
    try:
        eps = entry_points(group=PLUGIN_GROUP)
    except (TypeError, ImportError, AttributeError) as e:
        logging.warning(f"Error al obtener entry points: {e}")
        eps = entry_points().get(PLUGIN_GROUP, [])

    for ep in eps:
        instancia = cargar_plugin_seguro(ep.value)
        if instancia is not None:
            plugins.append(instancia)
    return plugins


def cargar_plugin_seguro(ruta: str) -> Optional[PluginInterface]:
    """Carga de forma segura un plugin a partir de ``modulo:Clase``.
    
    Args:
        ruta: Ruta al plugin en formato "modulo:Clase"
        
    Returns:
        Optional[PluginInterface]: Instancia del plugin o None si hay error
    """
    if not isinstance(ruta, str):
        logging.error(f"La ruta debe ser un string: {type(ruta)}")
        return None

    try:
        module_name, class_name = ruta.split(":", 1)
    except ValueError:
        logging.error(f"Ruta de plugin inválida: {ruta}")
        return None

    try:
        module = import_module(module_name)
    except Exception as exc:
        logging.error(f"Error importando módulo {module_name}: {exc}")
        return None

    try:
        plugin_cls = getattr(module, class_name)
    except AttributeError:
        logging.error(f"No se encontró la clase {class_name} en {module_name}")
        return None

    try:
        if not isinstance(plugin_cls, type) or not issubclass(plugin_cls, PluginInterface):
            logging.warning(f"El plugin {ruta} no implementa PluginInterface")
            return None
    except TypeError:
        logging.error(f"La clase {class_name} no es válida")
        return None

    try:
        instancia = plugin_cls()
    except Exception as exc:
        logging.error(f"Error instanciando plugin {ruta}: {exc}")
        return None

    if not getattr(instancia, "name", ""):
        logging.warning(f"Plugin {ruta} no define atributo name")
        return None

    version = getattr(instancia, "version", DEFAULT_VERSION)
    description = getattr(instancia, "description", DEFAULT_DESCRIPTION)
    registrar_plugin(instancia.name, version, description)
    return instancia


__all__ = [
    "PluginInterface",
    "PluginCommand",
    "descubrir_plugins",
    "cargar_plugin_seguro",
    "registrar_plugin",
    "obtener_registro",
    "obtener_registro_detallado",
]