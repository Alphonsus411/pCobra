"""Operaciones para proyectar holobits usando ``holobit-sdk``."""

from holobit_sdk.visualization.projector import proyectar_holograma
from holobit_sdk.core.quark import Quark
from holobit_sdk.core.holobit import Holobit as SDKHolobit

from core.holobits.holobit import Holobit
from core.holobits.graficar import _to_sdk_holobit


def proyectar(hb: Holobit, modo: str):
    """Proyecta un ``Holobit`` mediante ``holobit-sdk``."""
    if not isinstance(hb, Holobit):
        raise TypeError("proyectar espera una instancia de Holobit")
    sdk_hb = _to_sdk_holobit(hb)
    # El SDK no distingue modos actualmente; se grafica el resultado
    proyectar_holograma(sdk_hb)
    return None
