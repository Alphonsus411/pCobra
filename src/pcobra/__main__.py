"""Entrypoint de módulo para ``python -m pcobra``.

Este módulo delega explícitamente en :func:`pcobra.cli.main`, que es la ruta
oficial de inicialización de la CLI.
"""

from __future__ import annotations

import sys

from pcobra.cli import main


if __name__ == "__main__":
    sys.exit(main())
