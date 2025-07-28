import os
from pathlib import Path
import subprocess
from typing import Any, List
from argparse import _SubParsersAction

from cobra.cli.commands.base import BaseCommand
from cobra.cli.i18n import _
from cobra.cli.utils.messages import mostrar_error, mostrar_info

class EmpaquetarCommand(BaseCommand):
    """Empaqueta la CLI en un ejecutable."""
    name = "empaquetar"

    def register_subparser(self, subparsers: _SubParsersAction) -> Any:
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

    def run(self, args: Any) -> int:
        """Ejecuta la lógica del comando."""
        raiz = Path(__file__).resolve().parents[3]
        cli_path = raiz / "src" / "cli" / "cli.py"
        output = Path(args.output)
        nombre = args.name
        spec = getattr(args, "spec", None)
        datos = getattr(args, "add_data", [])

        # Validar directorio de salida
        try:
            output.mkdir(parents=True, exist_ok=True)
        except PermissionError:
            mostrar_error(_("No hay permisos para crear el directorio {dir}").format(
                dir=output))
            return 1

        # Validar que cli.py existe
        if not cli_path.exists():
            mostrar_error(_("No se encuentra el archivo CLI en {path}").format(
                path=cli_path))
            return 1

        try:
            cmd: List[str] = ["pyinstaller"]
            if spec:
                cmd.append(spec)
            else:
                cmd.extend(["--onefile", "-n", nombre, str(cli_path)])

            for d in datos:
                if ";" not in d:
                    mostrar_error(_("Formato inválido para --add-data: {data}").format(
                        data=d))
                    return 1
                cmd.extend(["--add-data", d])

            cmd.extend(["--distpath", str(output)])
            
            subprocess.run(cmd, check=True)
            
            ejecutable = output / nombre
            if not ejecutable.exists():
                mostrar_error(_("No se generó el ejecutable esperado"))
                return 1
                
            mostrar_info(
                _("Ejecutable generado en {path}").format(path=ejecutable)
            )
            return 0

        except FileNotFoundError:
            mostrar_error(
                _("No se encontró PyInstaller. Ejecuta 'pip install pyinstaller'.")
            )
            return 1
        except subprocess.CalledProcessError as e:
            mostrar_error(_("Error empaquetando la CLI: {err}").format(err=e))
            return 1