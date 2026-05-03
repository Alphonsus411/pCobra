"""Módulo canónico ``tiempo`` para `usar`.

Mantiene la API pública histórica (`ahora`, `formatear`, `dormir`) y delega
las operaciones de fecha/hora al backend oficial de ``standard_library.fecha``.
"""

from __future__ import annotations

import time
from datetime import datetime

from pcobra.standard_library.fecha import formatear as _formatear_fecha
from pcobra.standard_library.fecha import hoy as _hoy

__all__ = ["ahora", "formatear", "dormir"]


def ahora() -> datetime:
    """Devuelve la fecha y hora actual."""

    return _hoy()


def formatear(fecha: datetime, formato: str = "%Y-%m-%d %H:%M:%S") -> str:
    """Convierte *fecha* a texto según *formato*."""

    return _formatear_fecha(fecha, formato)


def dormir(segundos: float) -> None:
    """Detiene la ejecución durante *segundos*."""

    time.sleep(segundos)
