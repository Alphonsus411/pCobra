"""Ejemplos de transformaciones aplicables a un ``Holobit``."""

from .holobit import Holobit


def transformar(hb: Holobit, operacion: str, *parametros):
    """Funcion placeholder para transformar un Holobit."""
    if not isinstance(hb, Holobit):
        raise TypeError("transformar espera una instancia de Holobit")
    return f"Transformar {hb} con {operacion} {parametros}"
