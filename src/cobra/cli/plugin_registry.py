"""Registro en memoria de plugins y metadatos."""

_registry = {}


def registrar_plugin(nombre: str, version: str, description: str = "") -> None:
    """Registra un plugin con su versión y descripción."""
    _registry[nombre] = {"version": version, "description": description}


def obtener_registro():
    """Devuelve un diccionario nombre -> versión."""
    return {k: v["version"] for k, v in _registry.items()}


def obtener_registro_detallado():
    """Devuelve una copia completa del registro de plugins."""
    return {k: v.copy() for k, v in _registry.items()}


def limpiar_registro() -> None:
    """Limpia el registro de plugins (principalmente para pruebas)."""
    _registry.clear()
