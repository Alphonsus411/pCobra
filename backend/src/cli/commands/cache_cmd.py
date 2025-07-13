import os
from .base import BaseCommand
from ..i18n import _
from ..utils.messages import mostrar_info
from core.ast_cache import limpiar_cache


class CacheCommand(BaseCommand):
    """Limpia la cach\u00e9 del AST."""

    name = "cache"

    def register_subparser(self, subparsers):
        parser = subparsers.add_parser(
            self.name, help=_("Elimina los archivos del cach\u00e9 de AST")
        )
        parser.set_defaults(cmd=self)
        return parser

    def run(self, args):
        limpiar_cache()
        mostrar_info(_("Cach\u00e9 limpiada"))
        return 0
