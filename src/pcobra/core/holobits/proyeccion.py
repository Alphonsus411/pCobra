"""Operaciones para proyectar holobits usando ``holobit-sdk`` obligatorio en Python >=3.10."""

from __future__ import annotations

from .holobit import Holobit
from .graficar import _require_holobit_sdk, _to_sdk_holobit, proyectar_holograma


def proyectar(hb: Holobit, modo: str):
    """Proyecta un ``Holobit`` mediante ``holobit-sdk`` según el contrato soportado."""
    if not isinstance(hb, Holobit):
        raise TypeError("proyectar espera una instancia de Holobit")
    _require_holobit_sdk("proyectar")
    sdk_hb = _to_sdk_holobit(hb)
    # El SDK no distingue modos actualmente; se grafica el resultado
    proyectar_holograma(sdk_hb)
    return None
