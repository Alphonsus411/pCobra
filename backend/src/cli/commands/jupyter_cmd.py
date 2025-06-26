import subprocess
import sys
from .base import BaseCommand
from ..i18n import _
from ..utils.messages import mostrar_error


class JupyterCommand(BaseCommand):
    """Lanza Jupyter Notebook con el kernel Cobra instalado."""

    name = "jupyter"

    def register_subparser(self, subparsers):
        parser = subparsers.add_parser(self.name, help=_("Inicia Jupyter Notebook"))
        parser.set_defaults(cmd=self)
        return parser

    def run(self, args):
        try:
            subprocess.run([sys.executable, "-m", "cobra.jupyter_kernel", "install"], check=True)
            subprocess.run([
                "jupyter",
                "notebook",
                "--KernelManager.default_kernel_name=cobra",
            ], check=True)
            return 0
        except FileNotFoundError:
            mostrar_error(
                _(
                    "No se encontró el ejecutable 'jupyter'. Instala Jupyter para utilizar esta función."
                )
            )
            return 1
        except subprocess.CalledProcessError as e:
            mostrar_error(_("Error lanzando Jupyter: {err}").format(err=e))
            return 1
