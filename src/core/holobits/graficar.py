"""Funciones para graficar objetos ``Holobit`` utilizando ``holobit-sdk``."""

from core.holobits.holobit import Holobit
from holobit_sdk.visualization.projector import proyectar_holograma
from holobit_sdk.core.quark import Quark
from holobit_sdk.core.holobit import Holobit as SDKHolobit


def _to_sdk_holobit(hb: Holobit) -> SDKHolobit:
    """Convierte un :class:`Holobit` local a uno del SDK."""
    valores = list(hb.valores) + [0.0] * (6 - len(hb.valores))
    quarks = [Quark(v, 0, 0) for v in valores[:6]]
    antiquarks = [Quark(-q.posicion[0], -q.posicion[1], -q.posicion[2]) for q in quarks]
    return SDKHolobit(quarks, antiquarks)


def graficar(hb: Holobit):
    """Grafica un ``Holobit`` delegando en ``holobit-sdk``."""
    if not isinstance(hb, Holobit):
        raise TypeError("graficar espera una instancia de Holobit")
    sdk_hb = _to_sdk_holobit(hb)
    proyectar_holograma(sdk_hb)
    return None
