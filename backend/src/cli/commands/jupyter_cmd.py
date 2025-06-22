import subprocess
import sys
from .base import BaseCommand


class JupyterCommand(BaseCommand):
    """Lanza Jupyter Notebook con el kernel Cobra instalado."""

    name = "jupyter"

    def register_subparser(self, subparsers):
        parser = subparsers.add_parser(self.name, help="Inicia Jupyter Notebook")
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
        except subprocess.CalledProcessError as e:
            print(f"Error lanzando Jupyter: {e}")
            return 1
