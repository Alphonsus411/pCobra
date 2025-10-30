"""Punto de entrada ligero para ``python -m cobra.cli.cli``."""

from __future__ import annotations

import os
import sys

# Evita advertencias en tiempo de ejecución cuando la base de datos no está
# configurada explícitamente en el entorno.
os.environ.setdefault("SQLITE_DB_KEY", "cli-dev-key")

from pcobra.cobra.cli.cli import main as _pcobra_main


def main(argv=None):
    return _pcobra_main(argv)


if __name__ == "__main__":
    sys.exit(main())
