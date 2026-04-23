"""Shim histórico para el paquete de nivel superior ``cli``.

Permite ejecutar ``python -m cli.cli`` y ``import cli`` como compatibilidad
legacy sin colisionar con ``pcobra.cli`` durante la carga.
"""

from __future__ import annotations

import importlib
import warnings

_pcobra_cli = importlib.import_module("pcobra.cli")

import sys
sys.modules.setdefault("pcobra.cli", _pcobra_cli)

_pcobra_cli._activar_compatibilidad_legacy_si_corresponde("cli")

# Reexportar la API pública del módulo canónico.
from pcobra.cli import *  # noqa: F401,F403

warnings.warn(
    "`cli` es un shim legacy deprecado y no contractual; use `pcobra.cli`.",
    DeprecationWarning,
    stacklevel=2,
)
