import os
from typing import Any
from argparse import _SubParsersAction

from cobra.cli.commands.base import BaseCommand
from cobra.cli.i18n import _
from cobra.cli.utils.messages import mostrar_info, mostrar_error

class InitCommand(BaseCommand):
    """Inicializa un proyecto Cobra básico."""
    
    name = "init"

    def register_subparser(self, subparsers: _SubParsersAction) -> Any:
        """Registra los argumentos del subcomando.
        
        Args:
            subparsers: Objeto para registrar subcomandos
            
        Returns:
            El parser configurado para este subcomando
        """
        parser = subparsers.add_parser(
            self.name, help=_("Inicializa un proyecto Cobra")
        )
        parser.add_argument("ruta", help=_("Ruta donde crear el proyecto"))
        parser.set_defaults(cmd=self)
        return parser

    def run(self, args: Any) -> int:
        """Ejecuta la lógica del comando.
        
        Args:
            args: Argumentos parseados del comando
            
        Returns:
            int: 0 si la ejecución fue exitosa, 1 en caso de error
        """
        ruta = args.ruta
        
        try:
            # Crear directorio si no existe
            os.makedirs(ruta, exist_ok=True)
            
            # Crear archivo main.co
            main = os.path.join(ruta, "main.co")
            if not os.path.exists(main):
                with open(main, "w", encoding="utf-8") as f:
                    f.write("")
                    
            mostrar_info(_("Proyecto Cobra inicializado en {path}").format(path=ruta))
            return 0
            
        except PermissionError:
            mostrar_error(_("Error: No hay permisos para escribir en {path}").format(path=ruta))
            return 1
        except OSError as e:
            mostrar_error(_("Error al crear el proyecto: {err}").format(err=str(e)))
            return 1