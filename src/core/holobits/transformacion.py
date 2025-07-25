"""Transformaciones de ``Holobit`` a través de ``holobit-sdk``."""

from .holobit import Holobit
from holobit_sdk.core.holobit import Holobit as SDKHolobit

from .graficar import _to_sdk_holobit


def transformar(hb: Holobit, operacion: str, *parametros):
    """Aplica transformaciones utilizando ``holobit-sdk``."""
    if not isinstance(hb, Holobit):
        raise TypeError("transformar espera una instancia de Holobit")
    sdk_hb = _to_sdk_holobit(hb)
    if operacion == "rotar" and len(parametros) >= 2:
        eje, angulo = parametros[0], float(parametros[1])
        sdk_hb.rotar(eje, angulo)
    else:
        raise ValueError(f"Operacion no soportada: {operacion}")
    return None
