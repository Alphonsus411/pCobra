import logging
import os
from .base import BaseCommand

from src.core.interpreter import InterpretadorCobra
from src.core.lexer import Lexer
from src.core.parser import Parser
from src.core.semantic_validators import PrimitivaPeligrosaError, construir_cadena


class ExecuteCommand(BaseCommand):
    """Ejecuta un script Cobra desde un archivo."""

    name = "ejecutar"

    def register_subparser(self, subparsers):
        parser = subparsers.add_parser(self.name, help="Ejecuta un script Cobra")
        parser.add_argument("archivo")
        parser.set_defaults(cmd=self)
        return parser

    def run(self, args):
        archivo = args.archivo
        depurar = getattr(args, "depurar", False)
        formatear = getattr(args, "formatear", False)
        seguro = getattr(args, "seguro", False)

        if not os.path.exists(archivo):
            print(f"El archivo '{archivo}' no existe")
            return 1
        if formatear:
            self._formatear_codigo(archivo)
        if depurar:
            logging.getLogger().setLevel(logging.DEBUG)
        else:
            logging.getLogger().setLevel(logging.ERROR)

        with open(archivo, "r") as f:
            codigo = f.read()
        tokens = Lexer(codigo).tokenizar()
        ast = Parser(tokens).parsear()
        try:
            validador = construir_cadena()
            for nodo in ast:
                nodo.aceptar(validador)
        except PrimitivaPeligrosaError as pe:
            logging.error(f"Primitiva peligrosa: {pe}")
            print(f"Error: {pe}")
            return 1
        try:
            InterpretadorCobra(safe_mode=seguro).ejecutar_ast(ast)
            return 0
        except Exception as e:
            logging.error(f"Error ejecutando el script: {e}")
            print(f"Error ejecutando el script: {e}")
            return 1

    @staticmethod
    def _formatear_codigo(archivo):
        try:
            import subprocess

            subprocess.run([
                "black",
                archivo,
            ], check=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        except FileNotFoundError:
            print(
                "Herramienta de formateo no encontrada. Asegúrate de tener 'black' instalado."
            )
