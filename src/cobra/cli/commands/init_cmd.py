import os
from pathlib import Path
from argparse import ArgumentParser
from typing import Any

from cobra.cli.commands.base import BaseCommand
from cobra.cli.i18n import _
from cobra.cli.utils.argument_parser import CustomArgumentParser
from cobra.cli.utils.messages import mostrar_info, mostrar_error

class InitCommand(BaseCommand):
    """Inicializa un proyecto Cobra básico."""
    
    name = "init"

    def register_subparser(self, subparsers: Any) -> CustomArgumentParser:
        """Registra los argumentos del subcomando.
        
        Args:
            subparsers: Objeto para registrar subcomandos
            
        Returns:
            CustomArgumentParser: El parser configurado para este subcomando
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
        try:
            ruta = Path(args.ruta)
            ruta_abs = ruta.absolute()

            # Validar longitud de ruta
            if len(str(ruta_abs)) > 260:  # Límite Windows
                mostrar_error(_("Error: Ruta demasiado larga"))
                return 1

            # Validar caracteres no permitidos
            try:
                ruta_abs.resolve()
            except RuntimeError:
                mostrar_error(_("Error: La ruta contiene caracteres no válidos"))
                return 1

            # Crear directorio si no existe
            ruta.mkdir(parents=True, exist_ok=True)
            
            # Crear archivo main.co con template básico
            main = ruta / "main.co"
            if not main.exists():
                template = (
                    "# Proyecto Cobra\n"
                    "\n"
                    "func main() {\n"
                    "    # Tu código aquí\n"
                    "}\n"
                )
                main.write_text(template, encoding="utf-8")
                    
            mostrar_info(_("Proyecto Cobra inicializado en {path}").format(path=ruta))
            return 0
            
        except PermissionError:
            mostrar_error(_("Error: No hay permisos para escribir en {path}").format(path=ruta))
            return 1
        except FileExistsError:
            mostrar_error(_("Error: Ya existe un archivo con ese nombre"))
            return 1
        except NotADirectoryError:
            mostrar_error(_("Error: La ruta padre debe ser un directorio"))
            return 1
        except OSError as e:
            mostrar_error(_("Error al crear el proyecto: {err}").format(err=str(e)))
            return 1