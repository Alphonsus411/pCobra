"""Herramientas para trabajar con fechas y tiempos."""

from __future__ import annotations

from datetime import datetime, timedelta


def hoy() -> datetime:
    """Retorna la fecha y hora actual."""
    return datetime.now()


def formatear(fecha: datetime, formato: str = "%Y-%m-%d") -> str:
    """Convierte ``fecha`` a texto usando ``formato``."""
    return fecha.strftime(formato)


def sumar_dias(fecha: datetime, dias: int) -> datetime:
    """Devuelve una nueva fecha tras sumar ``dias`` a ``fecha``."""
    return fecha + timedelta(days=dias)

