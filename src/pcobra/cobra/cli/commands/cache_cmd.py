from typing import Any
import sqlite3

from pcobra.core.ast_cache import limpiar_cache
from pcobra.core.database import DatabaseDependencyError, DatabaseKeyError

from pcobra.cobra.cli.commands.base import BaseCommand
from pcobra.cobra.cli.i18n import _
from pcobra.cobra.cli.utils.argument_parser import CustomArgumentParser
from pcobra.cobra.cli.utils.messages import mostrar_info, mostrar_error


class CacheCommand(BaseCommand):
    """Limpia la caché del AST basada en la base de datos."""

    name: str = "cache"

    def register_subparser(self, subparsers: Any) -> CustomArgumentParser:
        """Registra los argumentos del subcomando."""

        parser = subparsers.add_parser(
            self.name, help=_("Elimina los archivos de la caché de AST")
        )
        parser.add_argument(
            "--vacuum",
            action="store_true",
            help=_(
                "Recompacta la base de datos SQLite después de limpiar la caché"
            ),
        )
        parser.set_defaults(cmd=self)
        return parser

    def run(self, args: Any) -> int:
        """Ejecuta la lógica del comando."""

        try:
            limpiar_cache(vacuum=getattr(args, "vacuum", False))
            mostrar_info(_("Caché limpiada exitosamente"))
            return 0
        except DatabaseKeyError:
            mostrar_error(
                _(
                    "No se configuró la clave 'SQLITE_DB_KEY' necesaria para acceder a la caché"
                )
            )
            return 1
        except DatabaseDependencyError as exc:
            mostrar_error(
                _("No fue posible inicializar la base de datos de caché: {error}").format(
                    error=str(exc)
                )
            )
            return 1
        except sqlite3.Error as exc:
            mostrar_error(
                _("Fallo de conexión con la base de datos de caché: {error}").format(
                    error=str(exc)
                )
            )
            return 1
