"""Módulo canónico ``tiempo`` para `usar`.

Mantiene la API pública histórica (`ahora`, `formatear`, `dormir`) y delega
las operaciones de fecha/hora al backend oficial de ``standard_library.fecha``.
"""

from __future__ import annotations

import time
from datetime import datetime

from pcobra.standard_library.fecha import formatear as _formatear_fecha
from pcobra.standard_library.fecha import hoy as _hoy

EQUIVALENCIAS_SEMANTICAS_TIEMPO: dict[str, str] = {
    "datetime.now": "ahora",
    "strftime": "formatear",
    "sleep": "dormir",
    "timestamp": "epoch",
    "fromtimestamp": "desde_epoch",
}

PUBLIC_API_TIEMPO: tuple[str, ...] = (
    "ahora",
    "formatear",
    "dormir",
    "epoch",
    "desde_epoch",
)


def ahora() -> datetime:
    """Devuelve la fecha y hora actual."""

    return _hoy()


def formatear(fecha: datetime, formato: str = "%Y-%m-%d %H:%M:%S") -> str:
    """Convierte *fecha* a texto según *formato*."""

    return _formatear_fecha(fecha, formato)


def dormir(segundos: float) -> None:
    """Detiene la ejecución durante *segundos*."""

    time.sleep(segundos)



def epoch(fecha: datetime | None = None) -> float:
    """Convierte una fecha a timestamp Unix en segundos."""

    return (fecha or ahora()).timestamp()


def desde_epoch(segundos: float) -> datetime:
    """Convierte segundos Unix a ``datetime`` local."""

    return datetime.fromtimestamp(segundos)


def _validar_superficie_publica_tiempo() -> None:
    if tuple(__all__) != PUBLIC_API_TIEMPO:
        raise RuntimeError(
            "[STARTUP CONTRACT] tiempo.__all__ debe exponer únicamente la API pública canónica de Cobra."
        )


__all__ = list(PUBLIC_API_TIEMPO)


_validar_superficie_publica_tiempo()
