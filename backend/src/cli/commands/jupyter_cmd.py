import subprocess
import sys
from .base import BaseCommand
from ..i18n import _
from ..utils.messages import mostrar_error


class JupyterCommand(BaseCommand):
    """Lanza Jupyter Notebook con el kernel Cobra instalado."""

    name = "jupyter"

    def register_subparser(self, subparsers):
        """Registra los argumentos del subcomando."""
        parser = subparsers.add_parser(self.name, help=_("Inicia Jupyter Notebook"))
        parser.add_argument(
            "--notebook",
            help=_("Ruta del cuaderno a abrir"),
        )
        parser.set_defaults(cmd=self)
        return parser

    def run(self, args):
        """Ejecuta la lógica del comando."""
        try:
            subprocess.run(
                [sys.executable, "-m", "cobra.jupyter_kernel", "install"], check=True
            )
            cmd = [
                "jupyter",
                "notebook",
                "--KernelManager.default_kernel_name=cobra",
            ]
            if args.notebook:
                cmd.append(args.notebook)
            subprocess.run(cmd, check=True)
            return 0
        except FileNotFoundError:
            mostrar_error(
                _(
                    "No se encontró el ejecutable 'jupyter'. Instala Jupyter "
                    "para utilizar esta función."
                )
            )
            return 1
        except subprocess.CalledProcessError as e:
            mostrar_error(_("Error lanzando Jupyter: {err}").format(err=e))
            return 1
