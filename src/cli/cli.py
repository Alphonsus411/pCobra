"""Shim histórico mínimo para ``python -m cli.cli``.

Ruta canónica runtime: ``src/pcobra/cobra/cli/cli.py``.
"""

from __future__ import annotations

import sys

import importlib

_pcobra_cli = importlib.import_module("pcobra.cli")
sys.modules.setdefault("pcobra.cli", _pcobra_cli)
from pcobra.cobra.cli.cli import main as _pcobra_main

_pcobra_cli._activar_compatibilidad_legacy_si_corresponde("cli.cli")


def main(argv: list[str] | None = None) -> int:
    """Delegar en el punto de entrada real de la CLI de Cobra."""

    sys.modules["pcobra.cli"] = _pcobra_cli
    resultado = _pcobra_main(argv)
    sys.modules["pcobra.cli"] = _pcobra_cli
    return resultado


if __name__ == "__main__":
    sys.exit(main())
