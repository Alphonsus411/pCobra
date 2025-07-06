from .base import BaseCommand
from ..i18n import _
from ..plugin_registry import obtener_registro_detallado
from ..utils.messages import mostrar_info


class PluginsCommand(BaseCommand):
    """Muestra los plugins instalados."""

    name = "plugins"

    def register_subparser(self, subparsers):
        parser = subparsers.add_parser(self.name, help=_("Lista plugins instalados"))
        parser.set_defaults(cmd=self)
        return parser

    def run(self, args):
        registro = obtener_registro_detallado()
        if not registro:
            mostrar_info(_("No hay plugins instalados"))
        else:
            for nombre, datos in registro.items():
                version = datos.get("version", "")
                descripcion = datos.get("description", "")
                if descripcion:
                    mostrar_info(f"{nombre} {version} - {descripcion}")
                else:
                    mostrar_info(f"{nombre} {version}")
        return 0

