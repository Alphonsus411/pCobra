import os
import subprocess

from .base import BaseCommand
from ..i18n import _
from ..utils.messages import mostrar_error, mostrar_info


class EmpaquetarCommand(BaseCommand):
    """Empaqueta la CLI en un ejecutable."""

    name = "empaquetar"

    def register_subparser(self, subparsers):
        parser = subparsers.add_parser(
            self.name, help=_("Crea un ejecutable para la CLI usando PyInstaller")
        )
        parser.add_argument(
            "--output",
            default="dist",
            help=_("Directorio donde colocar el ejecutable generado"),
        )
        parser.add_argument(
            "--name",
            default="cobra",
            help=_("Nombre del ejecutable resultante"),
        )
        parser.set_defaults(cmd=self)
        return parser

    def run(self, args):
        raiz = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "..", "..", "..")
        )
        cli_path = os.path.join(raiz, "backend", "src", "cli", "cli.py")
        output = args.output
        nombre = args.name
        try:
            subprocess.run(
                [
                    "pyinstaller",
                    "--onefile",
                    "-n",
                    nombre,
                    cli_path,
                    "--distpath",
                    output,
                ],
                check=True,
            )
            mostrar_info(
                _("Ejecutable generado en {path}").format(
                    path=os.path.join(output, nombre)
                )
            )
            return 0
        except FileNotFoundError:
            mostrar_error(
                _(
                    "PyInstaller no está instalado. Ejecuta 'pip install pyinstaller'."
                )
            )
            return 1
        except subprocess.CalledProcessError as e:
            mostrar_error(_("Error empaquetando la CLI: {err}").format(err=e))
            return 1
