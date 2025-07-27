import os

from cobra.cli.commands.base import BaseCommand
from cobra.cli.i18n import _
from cobra.cli.utils.messages import mostrar_error, mostrar_info


class CrearCommand(BaseCommand):
    """Crea archivos o proyectos Cobra con extensión .co."""

    name = "crear"

    def register_subparser(self, subparsers):
        """Registra los argumentos del subcomando."""
        parser = subparsers.add_parser(self.name, help=_("Crea archivos o proyectos"))
        sub = parser.add_subparsers(dest="accion")
        arch = sub.add_parser("archivo", help=_("Crea un archivo .co"))
        arch.add_argument("ruta")
        carp = sub.add_parser("carpeta", help=_("Crea una carpeta"))
        carp.add_argument("ruta")
        proy = sub.add_parser("proyecto", help=_("Crea un proyecto básico"))
        proy.add_argument("ruta")
        parser.set_defaults(cmd=self)
        return parser

    def run(self, args):
        """Ejecuta la lógica del comando."""
        accion = args.accion
        if accion == "archivo":
            return self._crear_archivo(args.ruta)
        elif accion == "carpeta":
            return self._crear_carpeta(args.ruta)
        elif accion == "proyecto":
            return self._crear_proyecto(args.ruta)
        else:
            mostrar_error(_("Acción no reconocida"))
            return 1

    @staticmethod
    def _crear_archivo(ruta):
        if not ruta.endswith(".co"):
            ruta += ".co"
        os.makedirs(os.path.dirname(ruta) or ".", exist_ok=True)
        with open(ruta, "w", encoding="utf-8"):
            pass
        mostrar_info(_("Archivo creado: {path}").format(path=ruta))
        return 0

    @staticmethod
    def _crear_carpeta(ruta):
        os.makedirs(ruta, exist_ok=True)
        mostrar_info(_("Carpeta creada: {path}").format(path=ruta))
        return 0

    @staticmethod
    def _crear_proyecto(ruta):
        os.makedirs(ruta, exist_ok=True)
        main = os.path.join(ruta, "main.co")
        with open(main, "w", encoding="utf-8"):
            pass
        mostrar_info(_("Proyecto Cobra creado en {path}").format(path=ruta))
        return 0
