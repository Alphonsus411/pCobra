from .base import BaseCommand
from ..utils.messages import mostrar_error


class FletCommand(BaseCommand):
    """Inicia el entorno IDLE basado en Flet."""

    name = "gui"

    def register_subparser(self, subparsers):
        parser = subparsers.add_parser(
            self.name, help="Inicia la interfaz gráfica"
        )
        parser.set_defaults(cmd=self)
        return parser

    def run(self, args):
        try:
            import flet
            from src.gui.idle import main
        except ModuleNotFoundError:
            mostrar_error("Flet no está instalado. Ejecuta 'pip install flet'.")
            return 1
        flet.app(target=main)
        return 0
