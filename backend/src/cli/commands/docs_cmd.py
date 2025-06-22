import os
import subprocess
from .base import BaseCommand


class DocsCommand(BaseCommand):
    """Genera la documentación HTML del proyecto."""

    name = "docs"

    def register_subparser(self, subparsers):
        parser = subparsers.add_parser(
            self.name, help="Genera la documentación del proyecto"
        )
        parser.set_defaults(cmd=self)
        return parser

    def run(self, args):
        raiz = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "..", "..", "..")
        )
        source = os.path.join(raiz, "frontend", "docs")
        build = os.path.join(raiz, "frontend", "build", "html")
        api = os.path.join(source, "api")
        codigo = os.path.join(raiz, "backend", "src")

        try:
            subprocess.run(["sphinx-apidoc", "-o", api, codigo], check=True)
            subprocess.run(["sphinx-build", "-b", "html", source, build], check=True)
            print(f"Documentación generada en {build}")
            return 0
        except subprocess.CalledProcessError as e:
            print(f"Error generando la documentación: {e}")
            return 1
