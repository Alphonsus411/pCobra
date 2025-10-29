"""Operaciones para proyectar holobits usando ``holobit-sdk``."""

from __future__ import annotations

from .holobit import Holobit
from .graficar import _to_sdk_holobit, proyectar_holograma


def proyectar(hb: Holobit, modo: str):
    """Proyecta un ``Holobit`` mediante ``holobit-sdk``."""
    if not isinstance(hb, Holobit):
        raise TypeError("proyectar espera una instancia de Holobit")
    sdk_hb = _to_sdk_holobit(hb)
    # El SDK no distingue modos actualmente; se grafica el resultado
    proyectar_holograma(sdk_hb)
    return None
