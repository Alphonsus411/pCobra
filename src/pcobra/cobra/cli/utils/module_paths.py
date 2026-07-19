"""Rutas compartidas por la gestión de módulos de la CLI."""

from pathlib import Path


def user_config_dir() -> Path:
    """Devuelve el directorio de configuración del usuario actual."""

    return Path.home() / ".cobra"


def modules_path() -> Path:
    """Devuelve el directorio de módulos sin crear rutas en disco."""

    return user_config_dir() / "modules"


USER_CONFIG_DIR = user_config_dir()
MODULES_PATH: Path = modules_path()
