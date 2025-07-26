import os
import subprocess

from src.cli.commands.base import BaseCommand
from src.cli.i18n import _
from src.cli.utils.messages import mostrar_error, mostrar_info


class DocsCommand(BaseCommand):
    """Genera la documentación HTML del proyecto."""

    name = "docs"

    def register_subparser(self, subparsers):
        """Registra los argumentos del subcomando."""
        parser = subparsers.add_parser(
            self.name, help=_("Genera la documentación del proyecto")
        )
        parser.set_defaults(cmd=self)
        return parser

    def run(self, args):
        """Ejecuta la lógica del comando."""
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
            mostrar_info(_("Documentación generada en {path}").format(path=build))
            return 0
        except FileNotFoundError:
            mostrar_error(_("Sphinx no está instalado. Ejecuta 'pip install sphinx'."))
            return 1
        except subprocess.CalledProcessError as e:
            mostrar_error(_("Error generando la documentación: {err}").format(err=e))
            return 1
