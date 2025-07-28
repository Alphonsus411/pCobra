import os
import subprocess
from pathlib import Path
from typing import Any
from argparse import _SubParsersAction

from cobra.cli.commands.base import BaseCommand
from cobra.cli.i18n import _
from cobra.cli.utils.messages import mostrar_error, mostrar_info

class ContainerCommand(BaseCommand):
    """Construye la imagen Docker del proyecto."""
    name = "contenedor"

    def register_subparser(self, subparsers: _SubParsersAction) -> Any:
        """Registra los argumentos del subcomando."""
        parser = subparsers.add_parser(self.name, help=_("Construye la imagen Docker"))
        parser.add_argument(
            "--tag",
            default="cobra",
            help=_("Nombre de la imagen"),
            type=str,
            pattern=r"^[a-zA-Z0-9_.-]+$"
        )
        parser.set_defaults(cmd=self)
        return parser

    def run(self, args: Any) -> int:
        """Ejecuta la lógica del comando."""
        try:
            raiz = Path(__file__).parents[4].resolve()
            
            subprocess.run(
                [
                    "docker",
                    "build",
                    "-t",
                    args.tag,
                    str(raiz)
                ],
                check=True,
                timeout=600  # 10 minutos máximo
            )
            mostrar_info(_("Imagen Docker creada"))
            return 0
            
        except FileNotFoundError:
            mostrar_error(
                _("Docker no está instalado. Por favor instala Docker desde docker.com")
            )
            return 1
        except subprocess.CalledProcessError as e:
            mostrar_error(_("Error construyendo la imagen Docker: {err}").format(err=e))
            return 1
        except subprocess.TimeoutExpired:
            mostrar_error(_("Tiempo de espera agotado al construir la imagen"))
            return 1
        except PermissionError:
            mostrar_error(_("Error de permisos al acceder al directorio del proyecto"))
            return 1