import os
import subprocess

from cobra.cli.commands.base import BaseCommand
from cobra.cli.i18n import _
from cobra.cli.utils.messages import mostrar_error, mostrar_info


class ContainerCommand(BaseCommand):
    """Construye la imagen Docker del proyecto."""

    name = "contenedor"

    def register_subparser(self, subparsers):
        """Registra los argumentos del subcomando."""
        parser = subparsers.add_parser(self.name, help=_("Construye la imagen Docker"))
        parser.add_argument("--tag", default="cobra", help=_("Nombre de la imagen"))
        parser.set_defaults(cmd=self)
        return parser

    def run(self, args):
        """Ejecuta la lógica del comando."""
        raiz = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "..", "..", "..")
        )
        try:
            subprocess.run(
                [
                    "docker",
                    "build",
                    "-t",
                    args.tag,
                    raiz,
                ],
                check=True,
            )
            mostrar_info(_("Imagen Docker creada"))
            return 0
        except FileNotFoundError:
            mostrar_error(
                _(
                    "Docker no está instalado. Ejecuta 'apt install docker' "
                    "u otra configuración."
                )
            )
            return 1
        except subprocess.CalledProcessError as e:
            mostrar_error(_("Error construyendo la imagen Docker: {err}").format(err=e))
            return 1
