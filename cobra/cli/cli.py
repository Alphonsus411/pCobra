"""Shim de compatibilidad para ``cobra.cli.cli`` en instalaciones legacy.

Ruta canónica: ``pcobra.cobra.cli.cli.main``.
Motivo del shim: mantener soporte temporal de imports/arranque heredados.
Garantías de compatibilidad:
- delegación total al entrypoint canónico;
- comportamiento uniforme con ``pcobra.cli``, ``cli`` y ``cobra.cli``;
- ejecución equivalente vía ``python -m cobra.cli.cli`` o archivo script.
"""

from __future__ import annotations

import importlib
import sys

_pcobra_cli = importlib.import_module("pcobra.cli")
sys.modules.setdefault("pcobra.cli", _pcobra_cli)
from pcobra.cobra.cli.cli import main as _pcobra_main

_pcobra_cli._activar_compatibilidad_legacy_si_corresponde("cobra.cli.cli")


def main(argv: list[str] | None = None) -> int:
    """Delega siempre en ``pcobra.cobra.cli.cli.main``."""

    return _pcobra_main(argv)


if __name__ == "__main__":
    sys.exit(main())
