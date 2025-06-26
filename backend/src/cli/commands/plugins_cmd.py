from .base import BaseCommand
from ..plugin_registry import obtener_registro


class PluginsCommand(BaseCommand):
    """Muestra los plugins instalados."""

    name = "plugins"

    def register_subparser(self, subparsers):
        parser = subparsers.add_parser(self.name, help="Lista plugins instalados")
        parser.set_defaults(cmd=self)
        return parser

    def run(self, args):
        registro = obtener_registro()
        if not registro:
            print("No hay plugins instalados")
        else:
            for nombre, version in registro.items():
                print(f"{nombre} {version}")
        return 0

