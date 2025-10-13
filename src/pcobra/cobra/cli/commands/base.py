from argparse import ArgumentParser
from typing import Any

from pcobra.cobra.cli.utils.argument_parser import CustomArgumentParser

class BaseCommand:
    """Clase base para subcomandos de la CLI."""
    
    #: Nombre del subcomando
    name: str = ""
    
    def __init__(self) -> None:
        """Inicializa el comando y valida el nombre.
        
        Raises:
            ValueError: Si el nombre del comando está vacío
        """
        if not self.name:
            raise ValueError("El nombre del comando no puede estar vacío")
    
    def register_subparser(self, subparsers: Any) -> CustomArgumentParser:
        """Registra los argumentos del subcomando en el parser.
        
        Args:
            subparsers: Objeto para registrar el subcomando
            
        Returns:
            CustomArgumentParser: El parser configurado para el subcomando
            
        Raises:
            NotImplementedError: Si la subclase no implementa este método
        """
        raise NotImplementedError
    
    def run(self, args: Any) -> int:
        """Ejecuta la lógica del comando.
        
        Args:
            args: Argumentos parseados del comando
            
        Returns:
            int: Código de salida (0 para éxito, otro valor para error)
            
        Raises:
            NotImplementedError: Si la subclase no implementa este método
        """
        raise NotImplementedError


class CommandError:
    pass