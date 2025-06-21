from .holobit import Holobit


def proyectar(hb: Holobit, modo: str):
    """Funcion placeholder para proyectar un Holobit."""
    if not isinstance(hb, Holobit):
        raise TypeError("proyectar espera una instancia de Holobit")
    return f"Proyectando {hb} en {modo}"
