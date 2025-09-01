import os
import platform
from pathlib import Path
import subprocess
import re
from typing import List, Any
from argparse import _ArgumentGroup

from cobra.cli.commands.base import BaseCommand
from cobra.cli.i18n import _
from cobra.cli.utils.argument_parser import CustomArgumentParser
from cobra.cli.utils.messages import mostrar_error, mostrar_info

class EmpaquetarCommand(BaseCommand):
    """Empaqueta la CLI en un ejecutable."""
    name = "empaquetar"

    def register_subparser(self, subparsers: _ArgumentGroup) -> CustomArgumentParser:
        """Registra los argumentos del subcomando.
        
        Args:
            subparsers: Grupo para registrar subcomandos
            
        Returns:
            CustomArgumentParser: El parser configurado para este subcomando
        """
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
            type=Path,
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

    def _validar_nombre(self, nombre: str) -> bool:
        """Valida que el nombre del ejecutable sea seguro.
        
        Args:
            nombre: Nombre del ejecutable a validar
            
        Returns:
            bool: True si el nombre es válido, False en caso contrario
        """
        patron = r'^[a-zA-Z0-9][a-zA-Z0-9_-]*$'
        return bool(re.match(patron, nombre))

    def _get_nombre_ejecutable(self, nombre_base: str) -> str:
        """Obtiene el nombre del ejecutable según la plataforma.
        
        Args:
            nombre_base: Nombre base del ejecutable
            
        Returns:
            str: Nombre del ejecutable con la extensión apropiada
        """
        if platform.system() == 'Windows':
            return f"{nombre_base}.exe"
        return nombre_base

    def _validar_add_data(self, dato: str) -> bool:
        """Valida un argumento --add-data.
        
        Args:
            dato: Argumento en formato 'src;dest'
            
        Returns:
            bool: True si el argumento es válido, False en caso contrario
        """
        try:
            src, _ = dato.split(';')
            src_path = Path(src)
            return src_path.exists() and src_path.is_file()
        except ValueError:
            return False

    def run(self, args: Any) -> int:
        """Ejecuta la lógica del comando.
        
        Args:
            args: Argumentos parseados del comando
            
        Returns:
            int: 0 si la ejecución fue exitosa, 1 en caso de error
        """
        if not self._validar_nombre(args.name):
            mostrar_error(_("Nombre de ejecutable inválido: {name}").format(
                name=args.name))
            return 1

        raiz = Path(__file__).resolve().parents[3]
        cli_path = raiz / "src" / "cli" / "cli.py"
        output = Path(args.output).resolve()
        nombre = self._get_nombre_ejecutable(args.name)
        spec = getattr(args, "spec", None)
        datos = getattr(args, "add_data", [])

        # Validar directorio de salida
        try:
            output.mkdir(parents=True, exist_ok=True)
            # Verificar permisos de escritura
            test_file = output / ".write_test"
            test_file.touch()
            test_file.unlink()
        except (PermissionError, OSError):
            mostrar_error(_("No hay permisos para escribir en el directorio {dir}").format(
                dir=output))
            return 1

        # Validar que cli.py existe
        if not cli_path.exists():
            mostrar_error(_("No se encuentra el archivo CLI en {path}").format(
                path=cli_path))
            return 1

        # Validar spec si se proporciona
        if spec and not spec.exists():
            mostrar_error(_("El archivo spec no existe: {path}").format(path=spec))
            return 1

        try:
            cmd: List[str] = ["pyinstaller"]
            if spec:
                cmd.append(str(spec))
            else:
                cmd.extend(["--onefile", "-n", nombre, str(cli_path)])

            for d in datos:
                if not self._validar_add_data(d):
                    mostrar_error(_("Formato o archivo inválido para --add-data: {data}").format(
                        data=d))
                    return 1
                cmd.extend(["--add-data", d])

            cmd.extend(["--distpath", str(output)])
            
            subprocess.run(cmd, check=True, capture_output=True, text=True)
            
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
            mostrar_error(_("Error empaquetando la CLI: {err}").format(
                err=e.stderr or str(e)))
            return 1