import subprocess
import sys
import shutil
from argparse import ArgumentParser
from pathlib import Path
from typing import Any

from pcobra.cobra.cli.commands.base import BaseCommand
from pcobra.cobra.cli.i18n import _
from pcobra.cobra.cli.utils.argument_parser import CustomArgumentParser
from pcobra.cobra.cli.utils.messages import mostrar_error
from pcobra.cobra.cli.utils.validators import validar_archivo_existente


class JupyterCommand(BaseCommand):
    """Lanza Jupyter Notebook con el kernel Cobra instalado."""
    name = "jupyter"

    class EjecutableNoEncontradoError(FileNotFoundError):
        """Error para indicar que no se pudo resolver un ejecutable requerido."""

    @staticmethod
    def _resolver_ejecutable(ejecutable: str) -> str:
        """Resuelve la ruta de un ejecutable con validaciones explícitas."""
        ejecutable_path = Path(ejecutable)
        if ejecutable_path.exists():
            return str(ejecutable_path.resolve())

        ejecutable_en_path = shutil.which(ejecutable)
        if not ejecutable_en_path:
            raise JupyterCommand.EjecutableNoEncontradoError(ejecutable)

        ejecutable_real = str(Path(ejecutable_en_path).resolve())
        if not Path(ejecutable_real).exists():
            raise JupyterCommand.EjecutableNoEncontradoError(ejecutable)
        return ejecutable_real

    def register_subparser(self, subparsers: Any) -> CustomArgumentParser:
        """Registra los argumentos del subcomando.

        Args:
            subparsers: Objeto para registrar el subcomando

        Returns:
            CustomArgumentParser: El parser configurado para este subcomando
        """
        parser = subparsers.add_parser(self.name, help=_("Inicia Jupyter Notebook"))
        parser.add_argument(
            "--notebook",
            help=_("Ruta del cuaderno a abrir"),
            type=Path,
        )
        parser.set_defaults(cmd=self)
        return parser

    def run(self, args: Any) -> int:
        """Ejecuta la lógica del comando.

        Args:
            args: Argumentos parseados del comando

        Returns:
            int: Código de salida (0 para éxito, otro valor para error)
        """
        try:
            # Verificar si jupyter está instalado
            import jupyter
        except ImportError:
            mostrar_error(
                _("No se encontró el módulo 'jupyter'. Instala Jupyter con 'pip install jupyter'")
            )
            return 1

        # Validar ruta del notebook si se proporciona
        if args.notebook:
            validar_archivo_existente(args.notebook)

        try:
            # Instalar el kernel de Cobra
            result = subprocess.run(
                [sys.executable, "-m", "pcobra.jupyter_kernel", "install"],
                check=True,
                capture_output=True,
                text=True
            )

            if result.returncode != 0:
                mostrar_error(_("Error al instalar el kernel canónico 'pcobra.jupyter_kernel': {err}").format(err=result.stderr))
                return 1

            python_executable = self._resolver_ejecutable(sys.executable)

            # Preparar comando de Jupyter
            cmd = [
                python_executable,
                "-m",
                "jupyter",
                "notebook",
                "--KernelManager.default_kernel_name=cobra",
            ]
            if args.notebook:
                cmd.append(str(args.notebook))

            # Ejecutar Jupyter
            subprocess.run(cmd, check=True)
            return 0

        except JupyterCommand.EjecutableNoEncontradoError:
            mostrar_error(
                _("No se encontró el ejecutable de Python para lanzar Jupyter. Verifica la instalación.")
            )
            return 1
        except subprocess.CalledProcessError as e:
            mostrar_error(_("Error lanzando Jupyter tras invocar el módulo canónico 'pcobra.jupyter_kernel': {err}").format(err=e))
            return 1
        except Exception as e:
            mostrar_error(_("Error inesperado: {err}").format(err=str(e)))
            return 1
