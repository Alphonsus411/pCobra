from typing import Any
from argparse import _SubParsersAction

from core.ast_cache import limpiar_cache
from cobra.cli.commands.base import BaseCommand
from cobra.cli.i18n import _
from cobra.cli.utils.messages import mostrar_info, mostrar_error

class CacheCommand(BaseCommand):
    """Limpia la caché del AST."""
    
    name: str = "cache"
    
    def register_subparser(self, subparsers: _SubParsersAction) -> Any:
        """Registra los argumentos del subcomando.
        
        Args:
            subparsers: Objeto para registrar el subcomando
            
        Returns:
            El parser configurado para el subcomando
        """
        parser = subparsers.add_parser(
            self.name, help=_("Elimina los archivos de la caché de AST")
        )
        parser.set_defaults(cmd=self)
        return parser

    def run(self, args: Any) -> int:
        """Ejecuta la lógica del comando.
        
        Args:
            args: Argumentos parseados del comando
            
        Returns:
            int: 0 si la operación fue exitosa, 1 en caso de error
            
        Raises:
            OSError: Si hay problemas al acceder al sistema de archivos
        """
        try:
            limpiar_cache()
            mostrar_info(_("Caché limpiada"))
            return 0
        except OSError as e:
            mostrar_error(f"Error al limpiar la caché: {e}")
            return 1