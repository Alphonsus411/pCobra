"""Shim histórico mínimo para ``python -m cli.cli``.

Ruta canónica runtime: ``src/pcobra/cobra/cli/cli.py``.
"""

from __future__ import annotations

import sys

from pcobra.cobra.cli.cli import main as _pcobra_main


def main(argv: list[str] | None = None) -> int:
    """Delegar en el punto de entrada real de la CLI de Cobra."""

    return _pcobra_main(argv)


if __name__ == "__main__":
    sys.exit(main())
