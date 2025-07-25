"""Transformaciones de ``Holobit`` a través de ``holobit-sdk``.

Si la versión instalada del SDK no dispone de las operaciones
``escalar`` o ``mover`` se aplican cálculos locales equivalentes.
"""

from .holobit import Holobit
from holobit_sdk.core.holobit import Holobit as SDKHolobit
import numpy as np

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


def escalar(hb: Holobit, factor: float):
    """Escala un ``Holobit`` usando ``holobit-sdk``."""
    if not isinstance(hb, Holobit):
        raise TypeError("escalar espera una instancia de Holobit")
    sdk_hb = _to_sdk_holobit(hb)
    if hasattr(sdk_hb, "escalar"):
        sdk_hb.escalar(float(factor))
    else:
        for q in sdk_hb.quarks + sdk_hb.antiquarks:
            q.posicion *= float(factor)
    return None


def mover(hb: Holobit, x: float, y: float, z: float):
    """Traslada un ``Holobit`` utilizando ``holobit-sdk``."""
    if not isinstance(hb, Holobit):
        raise TypeError("mover espera una instancia de Holobit")
    sdk_hb = _to_sdk_holobit(hb)
    if hasattr(sdk_hb, "mover"):
        sdk_hb.mover(float(x), float(y), float(z))
    else:
        delta = np.array([float(x), float(y), float(z)])
        for q in sdk_hb.quarks + sdk_hb.antiquarks:
            q.posicion += delta
    return None
