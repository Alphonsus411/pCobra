import logging

from ..i18n import _

RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RESET = "\033[0m"


def _mostrar(msg: str, nivel: str = "info") -> None:
    """Imprime el mensaje con color y registra el log correspondiente."""
    texto = _(msg)
    color = GREEN if nivel == "info" else YELLOW if nivel == "warning" else RED
    prefijos = {
        "warning": _("Advertencia"),
        "error": _("Error"),
    }
    prefijo = f"{prefijos[nivel]}: " if nivel in prefijos else ""
    print(f"{color}{prefijo}{texto}{RESET}")
    getattr(logging, nivel)(texto)


def mostrar_info(msg: str) -> None:
    """Muestra un mensaje informativo en verde."""
    _mostrar(msg, "info")


def mostrar_advertencia(msg: str) -> None:
    """Muestra un mensaje de advertencia en amarillo."""
    _mostrar(msg, "warning")


def mostrar_error(msg: str) -> None:
    """Muestra un mensaje de error en rojo."""
    _mostrar(msg, "error")


# Aliases para mantener compatibilidad con versiones anteriores.
info = mostrar_info
warning = mostrar_advertencia
error = mostrar_error
