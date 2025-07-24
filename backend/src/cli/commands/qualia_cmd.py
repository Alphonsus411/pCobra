import json
import os

from src.cli.commands.base import BaseCommand
from src.cli.i18n import _
from src.cli.utils.messages import mostrar_error, mostrar_info
from core import qualia_bridge


class QualiaCommand(BaseCommand):
    """Gestiona el estado del sistema Qualia."""

    name = "qualia"

    def register_subparser(self, subparsers):
        """Registra los argumentos del subcomando."""
        parser = subparsers.add_parser(
            self.name, help=_("Administra el estado de Qualia")
        )
        sub = parser.add_subparsers(dest="accion")
        sub.add_parser("mostrar", help=_("Muestra la base de conocimiento"))
        sub.add_parser("reiniciar", help=_("Elimina el estado guardado"))
        parser.set_defaults(cmd=self)
        return parser

    def run(self, args):
        """Ejecuta la lógica del comando."""
        accion = args.accion
        if accion == "mostrar":
            data = qualia_bridge.QUALIA.knowledge.as_dict()
            print(json.dumps(data, ensure_ascii=False, indent=2))
            return 0
        if accion == "reiniciar":
            state = qualia_bridge.STATE_FILE
            if os.path.exists(state):
                os.remove(state)
                mostrar_info(_("Estado de Qualia eliminado"))
            else:
                mostrar_info(_("No existe estado de Qualia"))
            return 0
        mostrar_error(_("Acción no reconocida"))
        return 1
