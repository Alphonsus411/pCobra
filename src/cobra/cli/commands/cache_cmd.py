from typing import Any
from argparse import ArgumentParser, _SubParsersAction  # TODO: Usar API pública
from core.ast_cache import limpiar_cache
from cobra.cli.commands.base import BaseCommand
from cobra.cli.i18n import _
from cobra.cli.utils.messages import mostrar_info, mostrar_error

class CacheCommand(BaseCommand):
    """Limpia la caché del AST.
    
    Este comando elimina todos los archivos temporales generados durante
    el análisis sintáctico de archivos Cobra.
    
    Raises:
        OSError: Si hay problemas de permisos o E/S al acceder al sistema de archivos
    """
    
    name: str = "cache"
    
    def register_subparser(self, subparsers: _SubParsersAction) -> ArgumentParser:
        """Registra los argumentos del subcomando.
        
        Args:
            subparsers: Objeto para registrar el subcomando
            
        Returns:
            ArgumentParser: El parser configurado para el subcomando
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
            mostrar_info(_("Caché limpiada exitosamente"))
            return 0
        except PermissionError:
            mostrar_error(_("Error de permisos al limpiar la caché"))
            return 1
        except OSError as e:
            mostrar_error(_("Error al limpiar la caché: {error}").format(error=str(e)))
            return 1