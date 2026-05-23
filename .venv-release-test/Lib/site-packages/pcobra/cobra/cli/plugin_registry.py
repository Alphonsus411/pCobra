"""Registro en memoria de plugins y metadatos."""
from threading import Lock
from packaging.version import InvalidVersion, Version


class PluginRegistryError(Exception):
    """Excepción base para errores del registro de plugins."""

    pass


_registry: dict[str, dict[str, str]] = {}
_lock = Lock()


def _version_es_valida(version: str) -> bool:
    """Comprueba si una versión cumple PEP 440."""
    try:
        Version(version)
    except InvalidVersion:
        return False
    return True


def registrar_plugin(nombre: str, version: str, description: str = "") -> None:
    """Registra un plugin con su versión y descripción.

    Args:
        nombre: Nombre único del plugin.
        version: Versión del plugin en formato PEP 440 (ej. ``1.0`` o ``1.2.3``).
        description: Descripción opcional del plugin.

    Raises:
        PluginRegistryError: Si el nombre/versión están vacíos o el plugin ya existe.
        ValueError: Si el formato de versión es inválido.
    """
    if not nombre or not version:
        raise PluginRegistryError("El nombre y versión no pueden estar vacíos")

    if not _version_es_valida(version):
        raise ValueError(
            f"La versión '{version}' es inválida; se esperaba formato compatible con PEP 440"
        )

    with _lock:
        if nombre in _registry:
            raise PluginRegistryError(f"Plugin '{nombre}' ya registrado")
        _registry[nombre] = {"version": version, "description": description}


def obtener_registro() -> dict[str, str]:
    """Devuelve un diccionario nombre -> versión (copia del estado actual).

    Returns:
        dict[str, str]: Copia del registro con nombres y versiones.
    """
    with _lock:
        return {k: v["version"] for k, v in _registry.items()}


def obtener_registro_detallado() -> dict[str, dict[str, str]]:
    """Devuelve una copia completa del registro de plugins.

    Cada entrada contiene las claves ``version`` y ``description``.

    Returns:
        dict[str, dict[str, str]]: Copia completa del registro.
    """
    with _lock:
        return {k: v.copy() for k, v in _registry.items()}


def limpiar_registro() -> None:
    """Limpia el registro de plugins (principalmente para pruebas)."""
    with _lock:
        _registry.clear()
