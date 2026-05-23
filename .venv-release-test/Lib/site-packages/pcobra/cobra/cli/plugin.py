"""Utilidades para la carga y registro de plugins de la CLI.

Este módulo combina las clases y funciones que antes estaban en
``plugin_interface`` y ``plugin_loader``. Se mantiene aquí para unificar la
API pública relacionada con plugins.
"""

import logging
import os
import hashlib
from abc import ABC, abstractmethod
from importlib import import_module
from importlib.util import source_from_cache
from importlib.metadata import entry_points
from dataclasses import dataclass
from typing import List, Optional, Any, Iterable
from argparse import ArgumentParser
from pathlib import Path

from pcobra.cobra.cli.commands.base import BaseCommand
from pcobra.cobra.cli.plugin_registry import (
    obtener_registro,
    obtener_registro_detallado,
    registrar_plugin,
)

# Constantes
DEFAULT_VERSION = "0.1"
DEFAULT_DESCRIPTION = ""
PLUGIN_GROUP = "cobra.plugins"
PLUGINS_ALLOWLIST_ENV = "COBRA_PLUGINS_ALLOWLIST"
PLUGINS_SAFE_MODE_ENV = "COBRA_PLUGINS_SAFE_MODE"


class PluginPolicyError(RuntimeError):
    """Error cuando un plugin incumple la política de confianza."""


@dataclass(frozen=True)
class PluginPolicy:
    """Política de confianza para carga de plugins.

    safe_mode=True implica bloqueo estricto de plugins no permitidos.
    """

    safe_mode: bool = True
    allowlist: tuple[str, ...] = ()


_PLUGIN_POLICY = PluginPolicy()


def _parse_allowlist(value: Optional[str]) -> tuple[str, ...]:
    if value is None:
        value = os.environ.get(PLUGINS_ALLOWLIST_ENV, "")
    return tuple(item.strip() for item in value.split(",") if item.strip())


def _is_truthy(value: str) -> bool:
    return value.strip().lower() in {"1", "true", "yes", "on"}


def configure_plugin_policy(
    safe_mode: Optional[bool] = None,
    allowlist: Optional[Iterable[str] | str] = None,
) -> PluginPolicy:
    """Configura la política global de plugins (flags/env)."""
    global _PLUGIN_POLICY
    if safe_mode is None:
        safe_mode = _is_truthy(os.environ.get(PLUGINS_SAFE_MODE_ENV, "1"))

    if allowlist is None or isinstance(allowlist, str):
        allowlist_values = _parse_allowlist(allowlist)
    else:
        allowlist_values = tuple(item.strip() for item in allowlist if item and item.strip())

    _PLUGIN_POLICY = PluginPolicy(safe_mode=bool(safe_mode), allowlist=allowlist_values)
    logging.getLogger(__name__).debug(
        (
            "Política de plugins configurada: safe_mode=%s allowlist=%s "
            "(sha256 valida únicamente el contenido del archivo real del módulo)"
        ),
        _PLUGIN_POLICY.safe_mode,
        list(_PLUGIN_POLICY.allowlist),
    )
    return _PLUGIN_POLICY


def get_plugin_policy() -> PluginPolicy:
    """Obtiene la política de plugins activa."""
    return _PLUGIN_POLICY


def _resolve_plugin_module(ruta: str) -> tuple[str, str, Any]:
    """Resuelve e importa un plugin declarado como ``modulo:Clase``."""
    module_name, class_name = ruta.split(":", 1)
    module = import_module(module_name)
    return module_name, class_name, module


def _read_module_file_bytes(module: Any) -> Optional[bytes]:
    """Lee bytes del archivo asociado al módulo (preferencia por fuente)."""
    module_file = getattr(module, "__file__", None)
    if not module_file:
        return None

    path = Path(module_file)
    if path.suffix == ".pyc":
        try:
            source_path = Path(source_from_cache(str(path)))
            if source_path.exists():
                path = source_path
        except (ValueError, OSError):
            pass

    try:
        return path.read_bytes()
    except OSError:
        return None


def _stable_sha256(value: bytes) -> str:
    """Calcula sha256 estable en hexadecimal minúscula."""
    return hashlib.sha256(value).hexdigest().lower()


def _plugin_allowed(ruta: str, module_name: str, module: Any) -> bool:
    policy = get_plugin_policy()
    if not policy.safe_mode:
        return True
    if not policy.allowlist:
        return False

    logger = logging.getLogger(__name__)
    module_bytes = _read_module_file_bytes(module)
    module_digest = _stable_sha256(module_bytes) if module_bytes is not None else None

    for rule in policy.allowlist:
        if rule.startswith("sha256:"):
            expected = rule.split(":", 1)[1].lower()
            if module_digest and module_digest == expected:
                return True
            if module_digest is None:
                logger.warning(
                    "Regla '%s' rechazada: no se pudo leer el archivo del módulo '%s' "
                    "para verificar sha256 de contenido.",
                    rule,
                    module_name,
                )
            continue
        if rule.startswith("prefix:") and module_name.startswith(rule.split(":", 1)[1]):
            return True
        if route_matches := (ruta == rule):
            return route_matches
        if module_name == rule:
            return True
    return False


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
    def register_subparser(self, subparsers: Any) -> None:
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

    def register_subparser(self, subparsers: Any) -> None:
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
        try:
            instancia = cargar_plugin_seguro(ep.value, origen=f"entry_point:{ep.name}")
            if instancia is not None:
                plugins.append(instancia)
        except PluginPolicyError:
            if get_plugin_policy().safe_mode:
                raise
            logging.warning("Plugin bloqueado por política (modo inseguro): %s", ep.value)
    return plugins


def cargar_plugin_seguro(ruta: str, origen: Optional[str] = None) -> Optional[PluginInterface]:
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
        _, _, module = _resolve_plugin_module(ruta)
    except Exception as exc:
        logging.error(f"Error importando módulo {module_name}: {exc}")
        return None

    module_file = getattr(module, "__file__", None)
    if not _plugin_allowed(ruta, module_name, module):
        msg = (
            f"Plugin '{ruta}' rechazado por política de confianza. "
            f"Se valida el sha256 del contenido de '{module_file or 'módulo_sin___file__'}' "
            f"(modo legado por sha256 de ruta retirado). "
            f"Configure {PLUGINS_ALLOWLIST_ENV} o desactive --plugins-safe-mode."
        )
        logging.error(msg)
        raise PluginPolicyError(msg)

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
    plugin_origin = getattr(module, "__file__", "origen_desconocido")
    logging.info(
        "AUDIT plugin_cargado nombre=%s version=%s origen=%s ruta=%s entrypoint=%s",
        instancia.name,
        version,
        plugin_origin,
        ruta,
        origen or "n/a",
    )
    return instancia


__all__ = [
    "PluginPolicy",
    "PluginPolicyError",
    "PLUGINS_ALLOWLIST_ENV",
    "PLUGINS_SAFE_MODE_ENV",
    "configure_plugin_policy",
    "get_plugin_policy",
    "PluginInterface",
    "PluginCommand",
    "descubrir_plugins",
    "cargar_plugin_seguro",
    "registrar_plugin",
    "obtener_registro",
    "obtener_registro_detallado",
]
