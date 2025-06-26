"""Registro en memoria de plugins y versiones."""

_registry = {}


def registrar_plugin(nombre: str, version: str) -> None:
    """Registra un plugin con su versión."""
    _registry[nombre] = version


def obtener_registro():
    """Devuelve una copia del registro de plugins."""
    return dict(_registry)


def limpiar_registro() -> None:
    """Limpia el registro de plugins (principalmente para pruebas)."""
    _registry.clear()
