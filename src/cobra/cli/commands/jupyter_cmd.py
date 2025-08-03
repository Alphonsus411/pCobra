import subprocess
import subprocess
import sys
from argparse import _SubParsersAction
from pathlib import Path
from typing import Any

from cobra.cli.commands.base import BaseCommand
from cobra.cli.i18n import _
from cobra.cli.utils.messages import mostrar_error


class JupyterCommand(BaseCommand):
    """Lanza Jupyter Notebook con el kernel Cobra instalado."""
    
    name = "jupyter"

    def register_subparser(self, subparsers: _SubParsersAction) -> Any:
        """Registra los argumentos del subcomando."""
        parser = subparsers.add_parser(self.name, help=_("Inicia Jupyter Notebook"))
        parser.add_argument(
            "--notebook",
            help=_("Ruta del cuaderno a abrir"),
            type=Path,
        )
        parser.set_defaults(cmd=self)
        return parser

    def run(self, args: Any) -> int:
        """Ejecuta la lógica del comando."""
        try:
            # Verificar si jupyter está instalado
            import jupyter
        except ImportError:
            mostrar_error(
                _("No se encontró el módulo 'jupyter'. Instala Jupyter con 'pip install jupyter'")
            )
            return 1

        # Validar ruta del notebook si se proporciona
        if args.notebook and not args.notebook.exists():
            mostrar_error(_("El archivo '{path}' no existe").format(path=args.notebook))
            return 1

        try:
            # Instalar el kernel de Cobra
            subprocess.run(
                [sys.executable, "-m", "cobra.jupyter_kernel", "install"], 
                check=True,
                capture_output=True,
                text=True
            )

            # Preparar comando de Jupyter
            cmd = [
                "jupyter",
                "notebook",
                "--KernelManager.default_kernel_name=cobra",
            ]
            if args.notebook:
                cmd.append(str(args.notebook))

            # Ejecutar Jupyter
            subprocess.run(cmd, check=True)
            return 0

        except FileNotFoundError:
            mostrar_error(
                _("No se encontró el ejecutable 'jupyter'. Verifica la instalación.")
            )
            return 1
        except subprocess.CalledProcessError as e:
            mostrar_error(_("Error lanzando Jupyter: {err}").format(err=e))
            return 1