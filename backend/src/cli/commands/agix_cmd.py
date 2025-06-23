import os
from .base import BaseCommand

from src.ia.analizador_agix import generar_sugerencias


class AgixCommand(BaseCommand):
    """Genera sugerencias para código Cobra usando agix."""

    name = "agix"

    def register_subparser(self, subparsers):
        parser = subparsers.add_parser(
            self.name, help="Analiza un archivo Cobra y sugiere mejoras"
        )
        parser.add_argument("archivo")
        parser.set_defaults(cmd=self)
        return parser

    def run(self, args):
        archivo = args.archivo
        if not os.path.exists(archivo):
            print(f"El archivo '{archivo}' no existe")
            return 1
        with open(archivo, "r") as f:
            codigo = f.read()
        sugerencias = generar_sugerencias(codigo)
        for s in sugerencias:
            print(s)
        return 0
