"""Punto de entrada ejecutable para ``python -m pcobra`` y ``python src/pcobra/__main__.py``."""

from __future__ import annotations

import sys
from pathlib import Path

if __package__ in {None, ""}:
    paquete_raiz = Path(__file__).resolve().parent.parent
    ruta_paquete = str(paquete_raiz)
    if ruta_paquete not in sys.path:
        sys.path.insert(0, ruta_paquete)
    __package__ = "pcobra"

from pcobra.cli import main


if __name__ == "__main__":
    sys.exit(main())
