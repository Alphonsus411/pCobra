"""Wrapper de compatibilidad para ``python -m cli.cli``."""

from __future__ import annotations

import os
import sys

# Garantiza que la base de datos tenga una clave por defecto cuando se ejecuta
# en entornos sin configuración previa (por ejemplo, durante los tests).
os.environ.setdefault("SQLITE_DB_KEY", "cli-dev-key")

from pcobra.cobra.cli.cli import main as _pcobra_main


def main(argv: list[str] | None = None) -> int:
    """Delegar en el punto de entrada real de la CLI de Cobra."""

    return _pcobra_main(argv)


if __name__ == "__main__":
    sys.exit(main())
