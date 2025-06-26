import logging
import os
from .base import BaseCommand
from ..utils.messages import mostrar_error, mostrar_info
from src.core.sandbox import ejecutar_en_sandbox

from src.core.interpreter import InterpretadorCobra
from src.cobra.lexico.lexer import Lexer
from src.cobra.parser.parser import Parser
from src.core.semantic_validators import PrimitivaPeligrosaError, construir_cadena


class ExecuteCommand(BaseCommand):
    """Ejecuta un script Cobra desde un archivo."""

    name = "ejecutar"

    def register_subparser(self, subparsers):
        parser = subparsers.add_parser(self.name, help="Ejecuta un script Cobra")
        parser.add_argument("archivo")
        parser.add_argument(
            "--sandbox",
            action="store_true",
            help="Ejecuta el código en una sandbox",
        )
        parser.set_defaults(cmd=self)
        return parser

    def run(self, args):
        archivo = args.archivo
        depurar = getattr(args, "depurar", False)
        formatear = getattr(args, "formatear", False)
        seguro = getattr(args, "seguro", False)
        extra_validators = getattr(args, "validadores_extra", None)
        sandbox = getattr(args, "sandbox", False)

        if not os.path.exists(archivo):
            mostrar_error(f"El archivo '{archivo}' no existe")
            return 1
        if formatear:
            self._formatear_codigo(archivo)
        if depurar:
            logging.getLogger().setLevel(logging.DEBUG)
        else:
            logging.getLogger().setLevel(logging.ERROR)

        with open(archivo, "r") as f:
            codigo = f.read()

        if sandbox:
            try:
                ejecutar_en_sandbox(codigo)
                return 0
            except Exception as e:
                logging.error(f"Error ejecutando en sandbox: {e}")
                mostrar_error(f"Error ejecutando en sandbox: {e}")
                return 1

        tokens = Lexer(codigo).tokenizar()
        ast = Parser(tokens).parsear()
        if seguro:
            try:
                validador = construir_cadena(
                    InterpretadorCobra._cargar_validadores(extra_validators)
                    if isinstance(extra_validators, str)
                    else extra_validators
                )
                for nodo in ast:
                    nodo.aceptar(validador)
            except PrimitivaPeligrosaError as pe:
                logging.error(f"Primitiva peligrosa: {pe}")
                mostrar_error(str(pe))
                return 1
        try:
            InterpretadorCobra(
                safe_mode=seguro,
                extra_validators=extra_validators,
            ).ejecutar_ast(ast)
            return 0
        except Exception as e:
            logging.error(f"Error ejecutando el script: {e}")
            mostrar_error(f"Error ejecutando el script: {e}")
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
            mostrar_error(
                "Herramienta de formateo no encontrada. "
                "Asegúrate de tener 'black' instalado."
            )
