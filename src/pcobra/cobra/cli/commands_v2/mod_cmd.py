from argparse import Namespace
from typing import Any

from pcobra.cobra.cli.commands.base import BaseCommand
from pcobra.cobra.cli.commands.modules_cmd import ModulesCommand
from pcobra.cobra.cli.i18n import _


class ModCommandV2(BaseCommand):
    """Comando v2 para gestión de módulos."""

    name = "mod"

    def __init__(self) -> None:
        super().__init__()
        self._legacy = ModulesCommand()

    def register_subparser(self, subparsers: Any):
        parser = subparsers.add_parser(self.name, help=_("Manage Cobra modules"))
        mod_sub = parser.add_subparsers(dest="action")

        mod_sub.add_parser("list", help=_("List modules"))

        install = mod_sub.add_parser("install", help=_("Install module from file"))
        install.add_argument("path", help=_("Path to module file"))

        remove = mod_sub.add_parser("remove", help=_("Remove an installed module"))
        remove.add_argument("name", help=_("Module name"))

        publish = mod_sub.add_parser("publish", help=_("Publish module to CobraHub"))
        publish.add_argument("path", help=_("Path to module file"))

        search = mod_sub.add_parser("search", help=_("Download module from CobraHub"))
        search.add_argument("name", help=_("Module name"))

        parser.set_defaults(cmd=self)
        return parser

    def run(self, args: Any) -> int:
        action_map = {
            "list": "listar",
            "install": "instalar",
            "remove": "remover",
            "publish": "publicar",
            "search": "buscar",
        }
        action = action_map.get(getattr(args, "action", ""), "")
        legacy_args = Namespace(
            accion=action,
            ruta=getattr(args, "path", None),
            nombre=getattr(args, "name", None),
        )
        return self._legacy.run(legacy_args)
