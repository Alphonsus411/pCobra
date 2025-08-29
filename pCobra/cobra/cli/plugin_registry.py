"""Registro en memoria de plugins y metadatos."""
from threading import Lock
from typing import Dict, Any

class PluginRegistryError(Exception):
    """Excepción base para errores del registro de plugins."""
    pass

_registry: Dict[str, Dict[str, str]] = {}
_lock = Lock()

def registrar_plugin(nombre: str, version: str, description: str = "") -> None:
    """Registra un plugin con su versión y descripción.
    
    Args:
        nombre: Nombre único del plugin
        version: Versión del plugin (formato: X.Y.Z)
        description: Descripción opcional del plugin
        
    Raises:
        PluginRegistryError: Si el nombre está vacío o el plugin ya existe
        ValueError: Si el formato de versión es inválido
    """
    if not nombre or not version:
        raise PluginRegistryError("El nombre y versión no pueden estar vacíos")
    
    with _lock:
        if nombre in _registry:
            raise PluginRegistryError(f"Plugin '{nombre}' ya registrado")
        _registry[nombre] = {
            "version": version,
            "description": description
        }

def obtener_registro() -> Dict[str, str]:
    """Devuelve un diccionario inmutable nombre -> versión.
    
    Returns:
        Dict[str, str]: Copia del registro con nombres y versiones
    """
    with _lock:
        return {k: v["version"] for k, v in _registry.items()}

def obtener_registro_detallado() -> Dict[str, Dict[str, str]]:
    """Devuelve una copia completa del registro de plugins.
    
    Returns:
        Dict[str, Dict[str, str]]: Copia completa del registro
    """
    with _lock:
        return {k: v.copy() for k, v in _registry.items()}

def limpiar_registro() -> None:
    """Limpia el registro de plugins (principalmente para pruebas)."""
    with _lock:
        _registry.clear()