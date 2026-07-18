"""Rutas compartidas por la gestión de módulos de la CLI."""

from pathlib import Path


USER_CONFIG_DIR = Path.home() / ".cobra"
MODULES_PATH: Path = USER_CONFIG_DIR / "modules"
