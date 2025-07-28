"""
Módulo de redirección para cobra.cli.
Este módulo actúa como un proxy para mantener la compatibilidad con importaciones existentes.
"""
import logging
from typing import Any

logger = logging.getLogger(__name__)

def _importar_y_transferir_atributos() -> None:
    """
    Importa el módulo cobra.cli y transfiere sus atributos al espacio de nombres actual.
    
    Raises:
        ImportError: Si no se puede importar el módulo cobra.cli
    """
    try:
        import cobra.cli
        
        # Transferir todos los atributos públicos
        for attr in dir(cobra.cli):
            if not attr.startswith('_'):
                globals()[attr] = getattr(cobra.cli, attr)
                
    except ImportError as e:
        logger.error("Error al importar cobra.cli: %s", str(e))
        raise ImportError(f"No se pudo importar el módulo cobra.cli: {e}") from e
    except Exception as e:
        logger.error("Error inesperado al importar cobra.cli: %s", str(e))
        raise

# Realizar la importación y transferencia de atributos
_importar_y_transferir_atributos()

# Limpiar la función del espacio de nombres global ya que no se necesita después de la inicialización
del _importar_y_transferir_atributos