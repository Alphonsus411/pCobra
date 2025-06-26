import os
from .base import BaseCommand
from ..utils.messages import mostrar_error, mostrar_info


class CrearCommand(BaseCommand):
    """Crea archivos o proyectos Cobra con extensión .co."""

    name = "crear"

    def register_subparser(self, subparsers):
        parser = subparsers.add_parser(self.name, help="Crea archivos o proyectos")
        sub = parser.add_subparsers(dest="accion")
        arch = sub.add_parser("archivo", help="Crea un archivo .co")
        arch.add_argument("ruta")
        carp = sub.add_parser("carpeta", help="Crea una carpeta")
        carp.add_argument("ruta")
        proy = sub.add_parser("proyecto", help="Crea un proyecto básico")
        proy.add_argument("ruta")
        parser.set_defaults(cmd=self)
        return parser

    def run(self, args):
        accion = args.accion
        if accion == "archivo":
            return self._crear_archivo(args.ruta)
        elif accion == "carpeta":
            return self._crear_carpeta(args.ruta)
        elif accion == "proyecto":
            return self._crear_proyecto(args.ruta)
        else:
            mostrar_error("Acción no reconocida")
            return 1

    @staticmethod
    def _crear_archivo(ruta):
        if not ruta.endswith(".co"):
            ruta += ".co"
        os.makedirs(os.path.dirname(ruta) or ".", exist_ok=True)
        with open(ruta, "w", encoding="utf-8"):
            pass
        mostrar_info(f"Archivo creado: {ruta}")
        return 0

    @staticmethod
    def _crear_carpeta(ruta):
        os.makedirs(ruta, exist_ok=True)
        mostrar_info(f"Carpeta creada: {ruta}")
        return 0

    @staticmethod
    def _crear_proyecto(ruta):
        os.makedirs(ruta, exist_ok=True)
        main = os.path.join(ruta, "main.co")
        with open(main, "w", encoding="utf-8"):
            pass
        mostrar_info(f"Proyecto Cobra creado en {ruta}")
        return 0
