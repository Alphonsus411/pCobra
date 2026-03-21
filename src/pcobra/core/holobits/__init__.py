"""API pública del runtime Python para objetos ``Holobit``.

El contrato Holobit transversal multi-backend incluye únicamente
``holobit``, ``proyectar``, ``transformar`` y ``graficar``. Los helpers
``escalar`` y ``mover`` se exportan aquí como capacidades adicionales del
runtime Python y no deben leerse como parte de la matriz contractual
multi-backend.
"""

from .holobit import Holobit
from .graficar import graficar
from .proyeccion import proyectar
from .transformacion import transformar, escalar, mover

__all__ = [
    "Holobit",
    "graficar",
    "proyectar",
    "transformar",
    "escalar",
    "mover",
]
