import logging
import os

from cobra.lexico.lexer import Lexer
from cobra.parser.parser import Parser
from cobra.transpilers import module_map
from core.interpreter import InterpretadorCobra
from core.sandbox import (
    ejecutar_en_contenedor,
    ejecutar_en_sandbox,
    validar_dependencias,
)
from core.semantic_validators import PrimitivaPeligrosaError, construir_cadena

from cobra.cli.commands.base import BaseCommand
from cobra.cli.i18n import _
from cobra.cli.utils.messages import mostrar_error, mostrar_info


class ExecuteCommand(BaseCommand):
    """Ejecuta un script Cobra desde un archivo."""

    name = "ejecutar"

    def register_subparser(self, subparsers):
        """Registra los argumentos del subcomando."""
        parser = subparsers.add_parser(self.name, help=_("Ejecuta un script Cobra"))
        parser.add_argument("archivo")
        parser.add_argument(
            "--sandbox",
            action="store_true",
            help=_("Ejecuta el código en una sandbox"),
        )
        parser.add_argument(
            "--contenedor",
            choices=["python", "js", "cpp", "rust"],
            help=_("Ejecuta el código en un contenedor Docker"),
        )
        parser.set_defaults(cmd=self)
        return parser

    def run(self, args):
        """Ejecuta la lógica del comando."""
        archivo = args.archivo
        depurar = getattr(args, "depurar", False)
        formatear = getattr(args, "formatear", False)
        seguro = getattr(args, "seguro", False)
        extra_validators = getattr(args, "validadores_extra", None)
        sandbox = getattr(args, "sandbox", False)
        contenedor = getattr(args, "contenedor", None)

        if not os.path.exists(archivo):
            mostrar_error(f"El archivo '{archivo}' no existe")
            return 1

        try:
            validar_dependencias("python", module_map.get_toml_map())
        except (ValueError, FileNotFoundError) as dep_err:
            mostrar_error(f"Error de dependencias: {dep_err}")
            return 1
        if formatear:
            self._formatear_codigo(archivo)
        if depurar:
            logging.getLogger().setLevel(logging.DEBUG)
        else:
            logging.getLogger().setLevel(logging.ERROR)

        with open(archivo, "r", encoding="utf-8") as f:
            codigo = f.read()

        if sandbox:
            try:
                ejecutar_en_sandbox(codigo)
                return 0
            except Exception as e:
                logging.error(f"Error ejecutando en sandbox: {e}")
                mostrar_error(f"Error ejecutando en sandbox: {e}")
                return 1

        if contenedor:
            try:
                salida = ejecutar_en_contenedor(codigo, contenedor)
                if salida:
                    mostrar_info(str(salida))
                return 0
            except Exception as e:
                logging.error(f"Error ejecutando en contenedor Docker: {e}")
                mostrar_error(f"Error ejecutando en contenedor Docker: {e}")
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

            subprocess.run(
                [
                    "black",
                    archivo,
                ],
                check=False,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
        except FileNotFoundError:
            mostrar_error(
                _(
                    "Herramienta de formateo no encontrada. Asegúrate de "
                    "tener 'black' instalado."
                )
            )
