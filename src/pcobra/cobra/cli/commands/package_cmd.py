from argparse import Namespace
from pathlib import Path
from typing import Any

from pcobra.cobra.cli.commands.base import BaseCommand
from pcobra.cobra.cli.i18n import _
from pcobra.cobra.cli.utils.argument_parser import CustomArgumentParser
from pcobra.cobra.cli.utils.messages import mostrar_error, mostrar_info
from pcobra.cobra.packaging import (
    DEFAULT_INSTALL_DIR,
    construir_paquete,
    crear_paquete,
    es_paquete_cobra,
    extraer_paquete,
    inspeccionar_paquete,
    validar_paquete,
)


class PaqueteCommand(BaseCommand):
    """Gestiona paquetes Cobra .co sin modificar la sintaxis del lenguaje."""

    name = "paquete"

    def register_subparser(self, subparsers: Any) -> CustomArgumentParser:
        parser = subparsers.add_parser(self.name, help=_("Gestiona paquetes Cobra .co"))
        sub = parser.add_subparsers(dest="accion", required=True)

        crear = sub.add_parser("crear", help=_("Crea la estructura de un paquete"))
        crear.add_argument("fuente", type=Path, help=_("Directorio del paquete"))
        crear.add_argument("paquete", nargs="?", type=Path, help=_("Alias legacy: salida .co opcional"))
        crear.add_argument("--nombre", default=None, help=_("Nombre del paquete"))
        crear.add_argument("--version", default="0.1.0", help=_("Versión"))

        validar = sub.add_parser("validar", help=_("Valida un paquete .co"))
        validar.add_argument("paquete", type=Path)

        construir = sub.add_parser("construir", help=_("Construye un paquete .co"))
        construir.add_argument("fuente", type=Path)
        construir.add_argument("salida", nargs="?", type=Path)
        construir.add_argument("--nombre", default=None)
        construir.add_argument("--version", default=None)

        inspeccionar = sub.add_parser("inspeccionar", help=_("Inspecciona el contenido de un paquete"))
        inspeccionar.add_argument("paquete", type=Path)

        extraer = sub.add_parser("extraer", help=_("Extrae un paquete .co"))
        extraer.add_argument("paquete", type=Path)
        extraer.add_argument("destino", type=Path)

        inst = sub.add_parser("instalar", help=_("Alias legacy de extraer a ~/.cobra/packages"))
        inst.add_argument("paquete", type=Path)
        inst.add_argument("--destino", type=Path, default=DEFAULT_INSTALL_DIR)

        parser.set_defaults(cmd=self)
        return parser

    def run(self, args: Namespace) -> int:
        try:
            if args.accion == "crear":
                nombre = args.nombre or args.fuente.name
                manifest = crear_paquete(args.fuente, nombre=nombre, version=args.version)
                if args.paquete:
                    destino = construir_paquete(args.fuente, args.paquete, nombre=nombre, version=args.version)
                    mostrar_info(_("Paquete creado en {dest}").format(dest=destino))
                else:
                    mostrar_info(_("Estructura de paquete creada: {manifest}").format(manifest=manifest))
                return 0
            if args.accion == "validar":
                if not es_paquete_cobra(args.paquete):
                    raise ValueError("No es un paquete Cobra: debe ser ZIP y contener cobra.pkg.json")
                validar_paquete(args.paquete)
                mostrar_info(_("Paquete válido: {pkg}").format(pkg=args.paquete))
                return 0
            if args.accion == "construir":
                destino = construir_paquete(args.fuente, args.salida, nombre=args.nombre, version=args.version)
                mostrar_info(_("Paquete construido en {dest}").format(dest=destino))
                return 0
            if args.accion == "inspeccionar":
                if not es_paquete_cobra(args.paquete):
                    raise ValueError("No es un paquete Cobra: debe ser ZIP y contener cobra.pkg.json")
                info = inspeccionar_paquete(args.paquete)
                mostrar_info(_("Paquete: {name} {version}").format(name=info.manifest.get("name"), version=info.manifest.get("version")))
                for file in info.files:
                    mostrar_info(f" - {file}")
                mostrar_info(_("SHA256: {checksum}").format(checksum=info.checksum))
                return 0
            if args.accion == "extraer":
                if not es_paquete_cobra(args.paquete):
                    raise ValueError("No es un paquete Cobra: debe ser ZIP y contener cobra.pkg.json")
                destino = extraer_paquete(args.paquete, args.destino)
                mostrar_info(_("Paquete extraído en {dest}").format(dest=destino))
                return 0
            if args.accion == "instalar":
                if not es_paquete_cobra(args.paquete):
                    raise ValueError("No es un paquete Cobra: debe ser ZIP y contener cobra.pkg.json")
                destino = extraer_paquete(args.paquete, args.destino)
                mostrar_info(_("Paquete instalado en {dest}").format(dest=destino))
                return 0
            mostrar_error(_("Acción de paquete no reconocida"))
            return 1
        except Exception as exc:
            mostrar_error(_("Error gestionando paquete: {error}").format(error=str(exc)))
            return 1
