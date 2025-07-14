import os

from .base import BaseCommand
from ..i18n import _
from ..utils.messages import mostrar_info


class InitCommand(BaseCommand):
    """Inicializa un proyecto Cobra básico."""

    name = "init"

    def register_subparser(self, subparsers):
        """Registra los argumentos del subcomando."""
        parser = subparsers.add_parser(
            self.name, help=_("Inicializa un proyecto Cobra")
        )
        parser.add_argument("ruta")
        parser.set_defaults(cmd=self)
        return parser

    def run(self, args):
        """Ejecuta la lógica del comando."""
        ruta = args.ruta
        os.makedirs(ruta, exist_ok=True)
        main = os.path.join(ruta, "main.co")
        if not os.path.exists(main):
            with open(main, "w", encoding="utf-8"):
                pass
        mostrar_info(
            _("Proyecto Cobra inicializado en {path}").format(path=ruta)
        )
        return 0
