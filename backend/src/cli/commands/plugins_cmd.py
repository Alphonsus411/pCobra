from .base import BaseCommand
from ..i18n import _
from ..plugin_registry import obtener_registro
from ..utils.messages import mostrar_info


class PluginsCommand(BaseCommand):
    """Muestra los plugins instalados."""

    name = "plugins"

    def register_subparser(self, subparsers):
        parser = subparsers.add_parser(self.name, help=_("Lista plugins instalados"))
        parser.set_defaults(cmd=self)
        return parser

    def run(self, args):
        registro = obtener_registro()
        if not registro:
            mostrar_info(_("No hay plugins instalados"))
        else:
            for nombre, version in registro.items():
                mostrar_info(f"{nombre} {version}")
        return 0

