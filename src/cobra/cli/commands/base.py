from argparse import _SubParsersAction
from typing import Any, NoReturn

class BaseCommand:
    """Clase base para subcomandos de la CLI."""

    #: Nombre del subcomando
    name: str = ""

    def __init__(self) -> None:
        """Inicializa el comando y valida el nombre."""
        if not self.name:
            raise ValueError("El nombre del comando no puede estar vacío")

    def register_subparser(self, subparsers: _SubParsersAction) -> Any:
        """Registra los argumentos del subcomando en el parser.

        Args:
            subparsers: Objeto _SubParsersAction para registrar el subcomando

        Returns:
            El parser configurado para el subcomando
        
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