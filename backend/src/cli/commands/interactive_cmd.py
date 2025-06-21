import logging
from .base import BaseCommand

from src.core.interpreter import InterpretadorCobra
from src.core.lexer import Lexer
from src.core.parser import Parser
from src.core.semantic_validators import PrimitivaPeligrosaError, construir_cadena


class InteractiveCommand(BaseCommand):
    """Modo interactivo del lenguaje Cobra."""

    name = "interactive"

    def register_subparser(self, subparsers):
        parser = subparsers.add_parser(self.name, help="Inicia el modo interactivo")
        parser.set_defaults(cmd=self)
        return parser

    def run(self, args):
        seguro = getattr(args, "seguro", False)
        interpretador = InterpretadorCobra(safe_mode=seguro)
        validador = construir_cadena()

        while True:
            try:
                linea = input("cobra> ").strip()
                if linea in ["salir", "salir()"]:
                    break
                elif linea == "tokens":
                    tokens = Lexer(linea).tokenizar()
                    print("Tokens generados:")
                    for token in tokens:
                        print(token)
                    continue
                elif linea == "ast":
                    tokens = Lexer(linea).tokenizar()
                    ast = Parser(tokens).parsear()
                    try:
                        for nodo in ast:
                            nodo.aceptar(validador)
                    except PrimitivaPeligrosaError as pe:
                        logging.error(f"Primitiva peligrosa: {pe}")
                        print(f"Error: {pe}")
                        continue
                    print("AST generado:")
                    print(ast)
                    continue
                elif linea:
                    tokens = Lexer(linea).tokenizar()
                    logging.debug(f"Tokens generados: {tokens}")
                    ast = Parser(tokens).parsear()
                    logging.debug(f"AST generado: {ast}")
                    try:
                        for nodo in ast:
                            nodo.aceptar(validador)
                    except PrimitivaPeligrosaError as pe:
                        logging.error(f"Primitiva peligrosa: {pe}")
                        print(f"Error: {pe}")
                        continue
                    interpretador.ejecutar_ast(ast)
            except SyntaxError as se:
                logging.error(f"Error de sintaxis: {se}")
                print(f"Error procesando la entrada: {se}")
            except RuntimeError as re:
                logging.error(f"Error crítico: {re}")
                print(f"Error crítico: {re}")
            except Exception as e:
                logging.error(f"Error general procesando la entrada: {e}")
                print(f"Error procesando la entrada: {e}")
