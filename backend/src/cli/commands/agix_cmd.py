import os
from .base import BaseCommand
from ..i18n import _
from ..utils.messages import mostrar_error, mostrar_info

from ia.analizador_agix import generar_sugerencias


class AgixCommand(BaseCommand):
    """Genera sugerencias para código Cobra usando agix."""

    name = "agix"

    def register_subparser(self, subparsers):
        parser = subparsers.add_parser(
            self.name, help=_("Analiza un archivo Cobra y sugiere mejoras")
        )
        parser.add_argument("archivo")
        parser.set_defaults(cmd=self)
        return parser

    def run(self, args):
        archivo = args.archivo
        if not os.path.exists(archivo):
            mostrar_error(f"El archivo '{archivo}' no existe")
            return 1
        with open(archivo, "r", encoding="utf-8") as f:
            codigo = f.read()
        sugerencias = generar_sugerencias(codigo)
        for s in sugerencias:
            mostrar_info(str(s))
        return 0
