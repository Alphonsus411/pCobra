from argparse import ArgumentParser
from typing import Any

from cobra.cli.commands.base import BaseCommand
from cobra.cli.i18n import _
from cobra.cli.utils.argument_parser import CustomArgumentParser
from cobra.cli.utils.messages import mostrar_error

class FletCommand(BaseCommand):
    """Inicia el entorno IDLE basado en Flet."""
    name = "gui"

    def __init__(self) -> None:
        """Inicializa el comando."""
        super().__init__()

    def register_subparser(self, subparsers: Any) -> CustomArgumentParser:
        """Registra los argumentos del subcomando.
        
        Args:
            subparsers: Objeto para registrar subcomandos
            
        Returns:
            El parser configurado para este subcomando
        """
        parser = subparsers.add_parser(self.name, help=_("Inicia la interfaz gráfica"))
        parser.set_defaults(cmd=self)
        return parser

    def run(self, args: Any) -> int:
        """Ejecuta la lógica del comando.
        
        Args:
            args: Argumentos parseados del comando
            
        Returns:
            int: 0 si la ejecución fue exitosa, 1 en caso de error
            
        Raises:
            ModuleNotFoundError: Si flet o gui.idle no están instalados
        """
        try:
            import flet
            from gui.idle import main
        except ModuleNotFoundError as e:
            mostrar_error(_("Error: {0}. Ejecuta 'pip install flet'.").format(str(e)))
            return 1
        except ImportError as e:
            mostrar_error(_("Error al importar módulos: {0}").format(str(e)))
            return 1
        
        try:
            flet.app(target=main)
            return 0
        except Exception as e:
            mostrar_error(_("Error inesperado al ejecutar la aplicación: {0}").format(str(e)))
            return 1