"""Funciones para cargar la configuración de la CLI de Cobra."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Dict

try:  # Python >= 3.11
    import tomllib
except ModuleNotFoundError:  # pragma: no cover
    import tomli as tomllib

DEFAULTS = {
    "language": "es",
    "default_command": "run",
    "log_format": "%(asctime)s - %(levelname)s - %(message)s",
    "log_formatter": "text",
    "program_name": "cobra",
}


def load_config() -> Dict[str, str]:
    """Carga la configuración para la CLI.

    Se busca un archivo ``cobra-cli.toml`` en el directorio actual y se
    permiten sobrescribir valores mediante variables de entorno.

    Returns:
        Dict[str, str]: Configuración con las claves ``language``,
        ``default_command``, ``log_format``, ``log_formatter`` y
        ``program_name``.
    """

    config = DEFAULTS.copy()
    cfg_path = Path("cobra-cli.toml")
    if cfg_path.exists():
        try:
            with cfg_path.open("rb") as f:
                data = tomllib.load(f)
            if isinstance(data, dict):
                for key in DEFAULTS:
                    if key in data:
                        config[key] = data[key]
        except (OSError, tomllib.TOMLDecodeError):  # pragma: no cover
            pass

    config["language"] = os.environ.get("COBRA_LANG", config["language"])
    config["default_command"] = os.environ.get(
        "COBRA_DEFAULT_COMMAND", config["default_command"]
    )
    config["log_format"] = os.environ.get("COBRA_LOG_FORMAT", config["log_format"])
    config["log_formatter"] = os.environ.get(
        "COBRA_LOG_FORMATTER", config["log_formatter"]
    )
    config["program_name"] = os.environ.get(
        "COBRA_PROGRAM_NAME", config["program_name"]
    )
    return config
