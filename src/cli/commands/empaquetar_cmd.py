import os
import subprocess

from src.cli.commands.base import BaseCommand
from src.cli.i18n import _
from src.cli.utils.messages import mostrar_error, mostrar_info


class EmpaquetarCommand(BaseCommand):
    """Empaqueta la CLI en un ejecutable."""

    name = "empaquetar"

    def register_subparser(self, subparsers):
        """Registra los argumentos del subcomando."""
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
        parser.add_argument(
            "--spec",
            help=_("Ruta al archivo .spec a utilizar"),
        )
        parser.add_argument(
            "--add-data",
            action="append",
            default=[],
            metavar="RUTA;DEST",
            help=_("Datos adicionales a incluir en formato 'src;dest'"),
        )
        parser.set_defaults(cmd=self)
        return parser

    def run(self, args):
        """Ejecuta la lógica del comando."""
        raiz = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "..", "..", "..")
        )
        cli_path = os.path.join(raiz, "backend", "src", "cli", "cli.py")
        output = args.output
        nombre = args.name
        spec = getattr(args, "spec", None)
        datos = getattr(args, "add_data", [])
        try:
            cmd = ["pyinstaller"]
            if spec:
                cmd.append(spec)
            else:
                cmd.extend(["--onefile", "-n", nombre, cli_path])
            for d in datos:
                cmd.extend(["--add-data", d])
            cmd.extend(["--distpath", output])
            subprocess.run(cmd, check=True)
            mostrar_info(
                _("Ejecutable generado en {path}").format(
                    path=os.path.join(output, nombre)
                )
            )
            return 0
        except FileNotFoundError:
            mostrar_error(
                _("PyInstaller no está instalado. Ejecuta 'pip install pyinstaller'.")
            )
            return 1
        except subprocess.CalledProcessError as e:
            mostrar_error(_("Error empaquetando la CLI: {err}").format(err=e))
            return 1
