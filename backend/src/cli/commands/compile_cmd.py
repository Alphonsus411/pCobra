import logging
import os
from .base import BaseCommand

from src.cobra.lexico.lexer import Lexer
from src.cobra.parser.parser import Parser
from src.core.semantic_validators import PrimitivaPeligrosaError, construir_cadena
from src.cobra.transpilers.transpiler.to_js import TranspiladorJavaScript
from src.cobra.transpilers.transpiler.to_python import TranspiladorPython
from src.cobra.transpilers.transpiler.to_asm import TranspiladorASM
from src.cobra.transpilers.transpiler.to_rust import TranspiladorRust
from src.cobra.transpilers.transpiler.to_cpp import TranspiladorCPP
from src.cobra.transpilers.transpiler.to_go import TranspiladorGo
from src.cobra.transpilers.transpiler.to_r import TranspiladorR
from src.cobra.transpilers.transpiler.to_julia import TranspiladorJulia
from src.cobra.transpilers.transpiler.to_ruby import TranspiladorRuby
from src.cobra.transpilers.transpiler.to_java import TranspiladorJava
from src.cobra.transpilers.transpiler.to_cobol import TranspiladorCOBOL
from src.cobra.transpilers.transpiler.to_fortran import TranspiladorFortran
from src.cobra.transpilers.transpiler.to_pascal import TranspiladorPascal


class CompileCommand(BaseCommand):
    """Transpila un archivo Cobra a distintos lenguajes.

    Soporta Python, JavaScript, ensamblador, Rust, C++, Go, R, Julia,
    Java y ahora también COBOL, Fortran y Pascal.
    """

    name = "compilar"

    def register_subparser(self, subparsers):
        parser = subparsers.add_parser(self.name, help="Transpila un archivo")
        parser.add_argument("archivo")
        parser.add_argument(
            "--tipo",
            choices=[
                "python",
                "js",
                "asm",
                "rust",
                "cpp",
                "go",
                "ruby",
                "r",
                "julia",
                "java",
                "cobol",
                "fortran",
                "pascal",
            ],
            default="python",
            help="Tipo de código generado",
        )
        parser.set_defaults(cmd=self)
        return parser

    def run(self, args):
        archivo = args.archivo
        transpilador = args.tipo
        if not os.path.exists(archivo):
            print(f"Error: El archivo '{archivo}' no existe.")
            return 1

        with open(archivo, "r") as f:
            codigo = f.read()
            try:
                tokens = Lexer(codigo).tokenizar()
                ast = Parser(tokens).parsear()

                validador = construir_cadena()
                for nodo in ast:
                    nodo.aceptar(validador)

                if transpilador == "python":
                    transp = TranspiladorPython()
                elif transpilador == "js":
                    transp = TranspiladorJavaScript()
                elif transpilador == "asm":
                    transp = TranspiladorASM()
                elif transpilador == "rust":
                    transp = TranspiladorRust()
                elif transpilador == "cpp":
                    transp = TranspiladorCPP()
                elif transpilador == "java":
                    transp = TranspiladorJava()
                elif transpilador == "go":
                    transp = TranspiladorGo()
                elif transpilador == "ruby":
                    transp = TranspiladorRuby()
                elif transpilador == "r":
                    transp = TranspiladorR()
                elif transpilador == "julia":
                    transp = TranspiladorJulia()
                elif transpilador == "cobol":
                    transp = TranspiladorCOBOL()
                elif transpilador == "fortran":
                    transp = TranspiladorFortran()
                elif transpilador == "pascal":
                    transp = TranspiladorPascal()
                else:
                    raise ValueError("Transpilador no soportado.")

                resultado = transp.transpilar(ast)
                print(f"Código generado ({transp.__class__.__name__}):")
                print(resultado)
                return 0
            except PrimitivaPeligrosaError as pe:
                logging.error(f"Primitiva peligrosa: {pe}")
                print(f"Error: {pe}")
                return 1
            except SyntaxError as se:
                logging.error(f"Error de sintaxis durante la transpilación: {se}")
                print(f"Error durante la transpilación: {se}")
                return 1
            except Exception as e:
                logging.error(f"Error general durante la transpilación: {e}")
                print(f"Error durante la transpilación: {e}")
                return 1
