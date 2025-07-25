import os

from ia.analizador_agix import generar_sugerencias

from src.cli.commands.base import BaseCommand
from src.cli.i18n import _
from src.cli.utils.messages import mostrar_error, mostrar_info


class AgixCommand(BaseCommand):
    """Genera sugerencias para código Cobra usando agix."""

    name = "agix"

    def register_subparser(self, subparsers):
        """Registra los argumentos del subcomando."""
        parser = subparsers.add_parser(
            self.name, help=_("Analiza un archivo Cobra y sugiere mejoras")
        )
        parser.add_argument("archivo")
        parser.set_defaults(cmd=self)
        return parser

    def run(self, args):
        """Ejecuta la lógica del comando."""
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
