"""Módulo principal para la entrada de la aplicación CLI."""
import logging
import sys
from typing import List, Optional

from dotenv import load_dotenv
from cobra.cli.cli import main as cli_main

logger = logging.getLogger(__name__)

def configurar_entorno() -> None:
    """
    Configura las variables de entorno desde el archivo .env si existe.
    
    El archivo .env debe contener pares clave=valor para configurar
    variables de entorno necesarias para la aplicación.
    
    Raises:
        FileNotFoundError: Si el archivo .env no existe
        PermissionError: Si no hay permisos para leer el archivo
    """
    try:
        load_dotenv()
    except (FileNotFoundError, PermissionError) as e:
        logger.error("Error al cargar variables de entorno: %s", str(e))
        raise
    except Exception as e:
        logger.critical("Error inesperado al cargar variables de entorno: %s", str(e))
        raise

def ejecutar_cli(argumentos: Optional[List[str]] = None) -> int:
    """
    Función principal que delega la ejecución en la CLI.
    
    Args:
        argumentos: Lista opcional de argumentos de línea de comandos.
                   Si es None, se utilizarán los argumentos del sistema.
    
    Returns:
        int: Código de salida de la ejecución.
            0: Ejecución exitosa
            1: Error durante la ejecución
    
    Raises:
        RuntimeError: Si ocurre un error durante la inicialización del CLI
    """
    try:
        configurar_entorno()
        return cli_main(argumentos)
    except Exception as e:
        logger.error("Error en la ejecución del CLI: %s", str(e))
        return 1

if __name__ == "__main__":
    sys.exit(ejecutar_cli())