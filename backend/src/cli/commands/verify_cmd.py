import os
import logging
from io import StringIO
from unittest.mock import patch

from .base import BaseCommand
from ..i18n import _
from ..utils.messages import mostrar_error, mostrar_info
from cli.commands.compile_cmd import TRANSPILERS
from core.interpreter import InterpretadorCobra
from cobra.lexico.lexer import Lexer
from cobra.parser.parser import Parser
from core.sandbox import ejecutar_en_sandbox, ejecutar_en_sandbox_js


class VerifyCommand(BaseCommand):
    """Verifica que la salida sea la misma en distintos lenguajes."""

    name = "verificar"

    def register_subparser(self, subparsers):
        """Registra los argumentos del subcomando."""
        parser = subparsers.add_parser(
            self.name,
            help=_("Comprueba la salida en varios lenguajes"),
        )
        parser.add_argument("archivo")
        parser.add_argument(
            "--lenguajes",
            "-l",
            required=True,
            help=_("Lista de lenguajes separados por comas"),
        )
        parser.set_defaults(cmd=self)
        return parser

    def run(self, args):
        """Ejecuta la lógica del comando."""
        archivo = args.archivo
        lenguajes = [l.strip() for l in args.lenguajes.split(",") if l.strip()]
        if not os.path.exists(archivo):
            mostrar_error(f"El archivo '{archivo}' no existe")
            return 1

        with open(archivo, "r", encoding="utf-8") as f:
            codigo = f.read()

        tokens = Lexer(codigo).tokenizar()
        ast = Parser(tokens).parsear()

        with patch("sys.stdout", new_callable=StringIO) as out:
            InterpretadorCobra().ejecutar_ast(ast)
        esperado = out.getvalue()

        diferencias = {}
        for lang in lenguajes:
            if lang not in ("python", "js"):
                mostrar_error(f"Lenguaje no soportado: {lang}")
                return 1
            transpiler = TRANSPILERS[lang]()
            try:
                codigo_gen = transpiler.generate_code(ast)
            except Exception as e:  # pylint: disable=broad-except
                logging.error("Error generando código para %s: %s", lang, e)
                diferencias[lang] = f"Error: {e}"
                continue
            try:
                if lang == "python":
                    salida = ejecutar_en_sandbox(codigo_gen)
                else:
                    salida = ejecutar_en_sandbox_js(codigo_gen)
            except Exception as e:  # pylint: disable=broad-except
                logging.error("Error ejecutando código para %s: %s", lang, e)
                diferencias[lang] = f"Error: {e}"
                continue
            if salida != esperado:
                diferencias[lang] = salida

        if diferencias:
            mostrar_error("Se encontraron diferencias:")
            for lang, salida in diferencias.items():
                mostrar_error(f"{lang}: {salida.strip()}")
            return 1

        mostrar_info("Todas las salidas coinciden")
        return 0
