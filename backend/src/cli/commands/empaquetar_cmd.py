import os
import subprocess

from .base import BaseCommand
from ..utils.messages import mostrar_error, mostrar_info


class EmpaquetarCommand(BaseCommand):
    """Empaqueta la CLI en un ejecutable."""

    name = "empaquetar"

    def register_subparser(self, subparsers):
        parser = subparsers.add_parser(
            self.name, help="Crea un ejecutable para la CLI usando PyInstaller"
        )
        parser.add_argument(
            "--output",
            default="dist",
            help="Directorio donde colocar el ejecutable generado",
        )
        parser.set_defaults(cmd=self)
        return parser

    def run(self, args):
        raiz = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "..", "..", "..")
        )
        cli_path = os.path.join(raiz, "backend", "src", "cli", "cli.py")
        output = args.output
        try:
            subprocess.run(
                [
                    "pyinstaller",
                    "--onefile",
                    "-n",
                    "cobra",
                    cli_path,
                    "--distpath",
                    output,
                ],
                check=True,
            )
            mostrar_info(f"Ejecutable generado en {os.path.join(output, 'cobra')}")
            return 0
        except FileNotFoundError:
            mostrar_error(
                "PyInstaller no está instalado. Ejecuta 'pip install pyinstaller'."
            )
            return 1
        except subprocess.CalledProcessError as e:
            mostrar_error(f"Error empaquetando la CLI: {e}")
            return 1
