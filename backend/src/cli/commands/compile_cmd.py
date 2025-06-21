import logging
import os
from .base import BaseCommand

from src.core.lexer import Lexer
from src.core.parser import Parser
from src.core.semantic_validator import PrimitivaPeligrosaError, ValidadorSemantico
from src.core.transpiler.to_js import TranspiladorJavaScript
from src.core.transpiler.to_python import TranspiladorPython


class CompileCommand(BaseCommand):
    """Transpila un archivo Cobra."""

    name = "compilar"

    def register_subparser(self, subparsers):
        parser = subparsers.add_parser(self.name, help="Transpila un archivo")
        parser.add_argument("archivo")
        parser.add_argument("--tipo", choices=["python", "js"], default="python")
        parser.set_defaults(cmd=self)
        return parser

    def run(self, args):
        archivo = args.archivo
        transpilador = args.tipo
        if not os.path.exists(archivo):
            print(f"Error: El archivo '{archivo}' no existe.")
            return

        with open(archivo, "r") as f:
            codigo = f.read()
            try:
                tokens = Lexer(codigo).tokenizar()
                ast = Parser(tokens).parsear()

                validador = ValidadorSemantico()
                for nodo in ast:
                    nodo.aceptar(validador)

                if transpilador == "python":
                    transp = TranspiladorPython()
                elif transpilador == "js":
                    transp = TranspiladorJavaScript()
                else:
                    raise ValueError("Transpilador no soportado.")

                resultado = transp.transpilar(ast)
                print(f"Código generado ({transp.__class__.__name__}):")
                print(resultado)
            except PrimitivaPeligrosaError as pe:
                logging.error(f"Primitiva peligrosa: {pe}")
                print(f"Error: {pe}")
            except SyntaxError as se:
                logging.error(f"Error de sintaxis durante la transpilación: {se}")
                print(f"Error durante la transpilación: {se}")
            except Exception as e:
                logging.error(f"Error general durante la transpilación: {e}")
                print(f"Error durante la transpilación: {e}")
