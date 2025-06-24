from .base import BaseCommand


class FletCommand(BaseCommand):
    """Inicia la interfaz gráfica utilizando Flet."""

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
            from src.gui.app import main
        except ModuleNotFoundError:
            print("Flet no está instalado. Ejecuta 'pip install flet'.")
            return 1
        flet.app(target=main)
        return 0
