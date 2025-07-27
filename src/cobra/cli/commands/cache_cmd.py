from core.ast_cache import limpiar_cache

from cobra.cli.commands.base import BaseCommand
from cobra.cli.i18n import _
from cobra.cli.utils.messages import mostrar_info


class CacheCommand(BaseCommand):
    """Limpia la cach\u00e9 del AST."""

    name = "cache"

    def register_subparser(self, subparsers):
        """Registra los argumentos del subcomando."""
        parser = subparsers.add_parser(
            self.name, help=_("Elimina los archivos del cach\u00e9 de AST")
        )
        parser.set_defaults(cmd=self)
        return parser

    def run(self, args):
        """Ejecuta la lógica del comando."""
        limpiar_cache()
        mostrar_info(_("Cach\u00e9 limpiada"))
        return 0
