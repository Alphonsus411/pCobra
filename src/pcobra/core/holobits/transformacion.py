"""Transformaciones y helpers del runtime Python para ``Holobit``.

``transformar`` forma parte del contrato Holobit transversal usado por los
transpiladores oficiales. En cambio, ``escalar`` y ``mover`` son helpers del
runtime Python: se exportan como API pública local, pero no pertenecen a la
matriz contractual multi-backend.

En Python ``>=3.10`` ``holobit-sdk`` forma parte del contrato obligatorio de
instalación de ``pcobra``. Cuando el SDK existe pero no expone métodos nativos
``escalar`` o ``mover``, estos helpers aplican un cálculo local equivalente
sobre la representación convertida al SDK.
"""

from pcobra._stubs.compat import import_optional_module

np = import_optional_module("numpy", safe_stub=True)

from .holobit import Holobit
from .graficar import _require_holobit_sdk, _to_sdk_holobit


def transformar(hb: Holobit, operacion: str, *parametros):
    """Aplica la transformación contractual soportada por el runtime Python."""
    if not isinstance(hb, Holobit):
        raise TypeError("transformar espera una instancia de Holobit")
    _require_holobit_sdk("transformar")
    sdk_hb = _to_sdk_holobit(hb)
    if operacion == "rotar" and len(parametros) >= 2:
        eje, angulo = parametros[0], float(parametros[1])
        sdk_hb.rotar(eje, angulo)
    else:
        raise ValueError(f"Operacion no soportada: {operacion}")
    return None


def escalar(hb: Holobit, factor: float):
    """Helper exclusivo del runtime Python para escalar un ``Holobit``."""
    if not isinstance(hb, Holobit):
        raise TypeError("escalar espera una instancia de Holobit")
    _require_holobit_sdk("escalar")
    sdk_hb = _to_sdk_holobit(hb)
    if hasattr(sdk_hb, "escalar"):
        sdk_hb.escalar(float(factor))
    else:
        for q in sdk_hb.quarks + sdk_hb.antiquarks:
            q.posicion *= float(factor)
    return None


def mover(hb: Holobit, x: float, y: float, z: float):
    """Helper exclusivo del runtime Python para trasladar un ``Holobit``."""
    if not isinstance(hb, Holobit):
        raise TypeError("mover espera una instancia de Holobit")
    _require_holobit_sdk("mover")
    sdk_hb = _to_sdk_holobit(hb)
    if hasattr(sdk_hb, "mover"):
        sdk_hb.mover(float(x), float(y), float(z))
    else:
        delta = np.array([float(x), float(y), float(z)])
        for q in sdk_hb.quarks + sdk_hb.antiquarks:
            q.posicion += delta
    return None
