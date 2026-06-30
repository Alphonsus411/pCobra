from argparse import Namespace
from pathlib import Path
from typing import Any

from pcobra.cobra.cli.cobrahub_client import CobraHubClient
from pcobra.cobra.cli.cobrahub_packages import CobraHubPackages
from pcobra.cobra.cli.commands.base import BaseCommand
from pcobra.cobra.cli.i18n import _
from pcobra.cobra.cli.utils.argument_parser import CustomArgumentParser
from pcobra.cobra.cli.utils.messages import mostrar_error, mostrar_info


class HubCommand(BaseCommand):
    """Publica, busca e instala paquetes en CobraHub."""

    name = "hub"

    def register_subparser(self, subparsers: Any) -> CustomArgumentParser:
        parser = subparsers.add_parser(
            self.name, help=_("Gestiona paquetes en CobraHub")
        )
        sub = parser.add_subparsers(dest="accion", required=True)
        pub = sub.add_parser("publicar", help=_("Publica un paquete .co"))
        pub.add_argument("paquete", type=Path)
        buscar = sub.add_parser("buscar", help=_("Busca paquetes"))
        buscar.add_argument("consulta")
        inst = sub.add_parser("instalar", help=_("Instala un paquete"))
        inst.add_argument("nombre")
        inst.add_argument("--version")
        inst.add_argument("--destino", type=Path)
        parser.set_defaults(cmd=self)
        return parser

    def run(self, args: Namespace) -> int:
        packages = CobraHubPackages(CobraHubClient())
        if args.accion == "publicar":
            return 0 if packages.publicar_paquete(str(args.paquete)) else 1
        if args.accion == "buscar":
            results = packages.buscar_paquetes(args.consulta)
            for item in results:
                nombre = item.get("name", item.get("nombre", "paquete"))
                mostrar_info(f"{nombre} {item.get('version', '')}".strip())
            return 0
        if args.accion == "instalar":
            destino = str(args.destino) if args.destino else None
            return 0 if packages.instalar_paquete(args.nombre, destino, args.version) else 1
        mostrar_error(_("Acción de hub no reconocida"))
        return 1
