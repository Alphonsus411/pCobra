"""Shim de compatibilidad para ``python -m cobra.cli.cli`` (layout ``src``).

Ruta canónica: ``pcobra.cobra.cli.cli.main``.
Motivo del shim: conservar la ruta histórica ``cobra.cli.cli`` durante la migración.
Garantías de compatibilidad:
- usa el mismo entrypoint canónico que el resto de wrappers;
- conserva ``pcobra.cli`` como módulo de referencia en runtime;
- ejecuta el mismo flujo tanto como módulo (``python -m``) como script.
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
