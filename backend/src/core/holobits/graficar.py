"""Funciones de ejemplo para graficar objetos ``Holobit``."""

from .holobit import Holobit


def graficar(hb: Holobit):
    """Funcion placeholder para graficar un Holobit."""
    if not isinstance(hb, Holobit):
        raise TypeError("graficar espera una instancia de Holobit")
    # Comportamiento simulado
    return f"Graficando {hb}"
