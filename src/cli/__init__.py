"""Punto de entrada de compatibilidad para ``cli``.

Permite ejecutar ``python -m cli.cli`` y otras importaciones heredadas que
asumen que ``cli`` es un paquete de nivel superior. Reexporta todas las
utilidades expuestas por :mod:`pcobra.cli` y registra alias en
``sys.modules`` para los submódulos relevantes.
"""

from __future__ import annotations

import importlib
import sys

from pcobra.cli import *  # noqa: F401,F403 - reexportado deliberadamente
from pcobra.cli import __all__  # type: ignore

_ALIASES = {
    "cli.cli": "pcobra.cobra.cli.cli",
    "cli.commands": "pcobra.cobra.cli.commands",
    "cli.utils": "pcobra.cobra.cli.utils",
    "cli.utils.semver": "pcobra.cobra.cli.utils.semver",
}

for alias, destino in _ALIASES.items():
    try:
        modulo = importlib.import_module(destino)
    except ModuleNotFoundError:  # pragma: no cover - alias opcional
        continue
    sys.modules.setdefault(alias, modulo)

