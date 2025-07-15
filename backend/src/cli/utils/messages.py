import logging

from ..i18n import _

RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RESET = "\033[0m"

# Flag global para habilitar o desactivar los colores.
USE_COLOR = True

# Logo ASCII mostrado al iniciar la CLI.
COBRA_LOGO = r"""
  ____        _               ____ _     ___
 / ___|___   | |__   ___ _ __/ ___| |   |_ _|
| |   / _ \  | '_ \ / _ \ '__| |   | |    | |
| |__| (_) | | |_) |  __/ |  | |___| |___ | |
 \____\___/  |_.__/ \___|_|   \____|_____|___|
"""


def disable_colors(disable: bool = True) -> None:
    """Activa o desactiva la salida de colores."""
    global USE_COLOR
    USE_COLOR = not disable


def mostrar_logo() -> None:
    """Muestra el logo de Cobra en verde."""
    color = GREEN if USE_COLOR else ""
    reset = RESET if USE_COLOR else ""
    print(f"{color}{COBRA_LOGO}{reset}")


def _mostrar(msg: str, nivel: str = "info") -> None:
    """Imprime el mensaje con color y registra el log correspondiente."""
    texto = _(msg)
    if USE_COLOR:
        color = GREEN if nivel == "info" else YELLOW if nivel == "warning" else RED
        reset = RESET
    else:
        color = ""
        reset = ""
    prefijos = {
        "warning": _("Advertencia"),
        "error": _("Error"),
    }
    prefijo = f"{prefijos[nivel]}: " if nivel in prefijos else ""
    print(f"{color}{prefijo}{texto}{reset}")
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
