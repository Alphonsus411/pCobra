"""
Módulo para manejo de mensajes y logging con soporte de colores en la CLI de Cobra.
"""

import logging
from enum import Enum
from typing import Final, Literal, Dict, Optional
from dataclasses import dataclass
from contextlib import contextmanager

try:
    from cobra.cli.i18n import _
except ImportError:
    # Fallback si el módulo de internacionalización no está disponible
    def _(text: str) -> str:
        return text

# Definición de tipos
LogLevel = Literal["info", "warning", "error"]

class ColorCode(Enum):
    """Códigos ANSI para colores."""
    RED: Final = "\033[91m"
    GREEN: Final = "\033[92m"
    YELLOW: Final = "\033[93m"
    RESET: Final = "\033[0m"

@dataclass
class MessageConfig:
    """Configuración para el manejo de mensajes."""
    use_color: bool = True
    
    def __post_init__(self) -> None:
        self._validate()
    
    def _validate(self) -> None:
        if not isinstance(self.use_color, bool):
            raise TypeError("use_color debe ser un booleano")

# Instancia global de configuración
config = MessageConfig()

# Logo ASCII mostrado al iniciar la CLI
COBRA_LOGO: Final = r"""
  ____        _               ____ _     ___
 / ___|___   | |__   ___ _ __/ ___| |   |_ _|
| |   / _ \  | '_ \ / _ \ '__| |   | |    | |
| |__| (_) | | |_) |  __/ |  | |___| |___ | |
 \____\___/  |_.__/ \___|_|   \____|_____|___|
"""

@contextmanager
def color_disabled():
    """Contexto para deshabilitar temporalmente los colores."""
    previous = config.use_color
    config.use_color = False
    try:
        yield
    finally:
        config.use_color = previous

def disable_colors(disable: bool = True) -> None:
    """
    Activa o desactiva la salida de colores.
    
    Args:
        disable: True para desactivar colores, False para activarlos
    """
    config.use_color = not disable

def mostrar_logo() -> None:
    """Muestra el logo de Cobra en verde."""
    color = ColorCode.GREEN.value if config.use_color else ""
    reset = ColorCode.RESET.value if config.use_color else ""
    print(f"{color}{COBRA_LOGO}{reset}")

def _mostrar(msg: str, nivel: LogLevel = "info") -> None:
    """
    Imprime el mensaje con color y registra el log correspondiente.
    
    Args:
        msg: Mensaje a mostrar
        nivel: Nivel del mensaje ('info', 'warning', 'error')
    
    Raises:
        ValueError: Si el nivel no es válido
    """
    if nivel not in ("info", "warning", "error"):
        raise ValueError(f"Nivel de log inválido: {nivel}")

    try:
        texto = _(msg)
        
        # Determinar el color según el nivel
        color_map: Dict[LogLevel, ColorCode] = {
            "info": ColorCode.GREEN,
            "warning": ColorCode.YELLOW,
            "error": ColorCode.RED
        }
        
        color = color_map[nivel].value if config.use_color else ""
        reset = ColorCode.RESET.value if config.use_color else ""
        
        # Prefijos para los diferentes niveles
        prefijos: Dict[LogLevel, str] = {
            "warning": _("Advertencia"),
            "error": _("Error")
        }
        
        prefijo = f"{prefijos[nivel]}: " if nivel in prefijos else ""
        print(f"{color}{prefijo}{texto}{reset}")
        
        # Registrar en el log
        log_func = getattr(logging, nivel)
        log_func(texto)
    except AttributeError:
        logging.error(f"Error al registrar mensaje con nivel: {nivel}")
    except Exception as e:
        logging.error(f"Error al mostrar mensaje: {str(e)}")

def mostrar_info(msg: str) -> None:
    """
    Muestra un mensaje informativo en verde.
    
    Args:
        msg: Mensaje a mostrar
    """
    _mostrar(msg, "info")

def mostrar_advertencia(msg: str) -> None:
    """
    Muestra un mensaje de advertencia en amarillo.
    
    Args:
        msg: Mensaje a mostrar
    """
    _mostrar(msg, "warning")

def mostrar_error(msg: str) -> None:
    """
    Muestra un mensaje de error en rojo.
    
    Args:
        msg: Mensaje a mostrar
    """
    _mostrar(msg, "error")

# Aliases para mantener compatibilidad con versiones anteriores
info = mostrar_info
warning = mostrar_advertencia
error = mostrar_error