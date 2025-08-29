"""Utilidades relacionadas con el tiempo."""

import time
from datetime import datetime


def ahora() -> datetime:
    """Devuelve la fecha y hora actual."""
    return datetime.now()


def formatear(fecha: datetime, formato: str = "%Y-%m-%d %H:%M:%S") -> str:
    """Convierte *fecha* a texto según *formato*."""
    return fecha.strftime(formato)


def dormir(segundos: float) -> None:
    """Detiene la ejecución durante *segundos*."""
    time.sleep(segundos)
