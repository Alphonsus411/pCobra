from .base import BaseCommand
from ..i18n import _
from ..plugin_registry import obtener_registro_detallado
from ..utils.messages import mostrar_info


class PluginsCommand(BaseCommand):
    """Muestra los plugins instalados."""

    name = "plugins"

    def register_subparser(self, subparsers):
        """Registra los argumentos del subcomando."""
        parser = subparsers.add_parser(self.name, help=_("Lista plugins instalados"))
        sub = parser.add_subparsers(dest="accion")
        bus = sub.add_parser(
            "buscar", help=_("Filtra plugins por nombre o descripción")
        )
        bus.add_argument("texto")
        parser.set_defaults(cmd=self, accion=None)
        return parser

    def run(self, args):
        """Ejecuta la lógica del comando."""
        registro = obtener_registro_detallado()
        if not registro:
            mostrar_info(_("No hay plugins instalados"))
            return 0

        accion = getattr(args, "accion", None)
        if accion == "buscar":
            texto = args.texto.lower()
            registro = {
                n: d
                for n, d in registro.items()
                if texto in n.lower()
                or texto in d.get("description", "").lower()
            }

        for nombre, datos in registro.items():
            version = datos.get("version", "")
            descripcion = datos.get("description", "")
            if descripcion:
                mostrar_info(f"{nombre} {version} - {descripcion}")
            else:
                mostrar_info(f"{nombre} {version}")
        return 0

