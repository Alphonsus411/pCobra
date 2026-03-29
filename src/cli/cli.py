"""Shim de compatibilidad para ``python -m cli.cli``.

Ruta canónica: ``pcobra.cobra.cli.cli.main``.
Motivo del shim: mantener operativos entrypoints legacy sin duplicar lógica.
Garantías de compatibilidad:
- conserva ``pcobra.cli`` registrado en ``sys.modules``;
- activa la política legacy de ``pcobra.cli`` para ``cli.cli``;
- funciona igual al ejecutar como módulo (``python -m cli.cli``) o script.
"""

from __future__ import annotations

import importlib
import sys

_pcobra_cli = importlib.import_module("pcobra.cli")
sys.modules.setdefault("pcobra.cli", _pcobra_cli)
from pcobra.cobra.cli.cli import main as _pcobra_main

_pcobra_cli._activar_compatibilidad_legacy_si_corresponde("cli.cli")


def main(argv: list[str] | None = None) -> int:
    """Delega siempre en ``pcobra.cobra.cli.cli.main``."""

    return _pcobra_main(argv)


if __name__ == "__main__":
    sys.exit(main())
