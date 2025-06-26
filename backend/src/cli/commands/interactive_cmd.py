import logging
from .base import BaseCommand
from ..utils.messages import mostrar_error, mostrar_info
from src.core.sandbox import ejecutar_en_sandbox

from src.core.interpreter import InterpretadorCobra
from src.core.qualia_bridge import get_suggestions
from src.cobra.lexico.lexer import Lexer
from src.cobra.parser.parser import Parser
from src.core.semantic_validators import PrimitivaPeligrosaError, construir_cadena


class InteractiveCommand(BaseCommand):
    """Modo interactivo del lenguaje Cobra."""

    name = "interactive"

    def register_subparser(self, subparsers):
        parser = subparsers.add_parser(self.name, help="Inicia el modo interactivo")
        parser.add_argument(
            "--sandbox",
            action="store_true",
            help="Ejecuta cada línea dentro de una sandbox",
        )
        parser.set_defaults(cmd=self)
        return parser

    def run(self, args):
        seguro = getattr(args, "seguro", False)
        extra_validators = getattr(args, "validadores_extra", None)
        sandbox = getattr(args, "sandbox", False)
        interpretador = InterpretadorCobra(
            safe_mode=seguro, extra_validators=extra_validators
        )
        validador = (
            construir_cadena(
                InterpretadorCobra._cargar_validadores(extra_validators)
                if isinstance(extra_validators, str)
                else extra_validators
            )
            if seguro
            else None
        )

        while True:
            try:
                linea = input("cobra> ").strip()
                if linea in ["salir", "salir()"]:
                    break
                elif linea == "tokens":
                    tokens = Lexer(linea).tokenizar()
                    mostrar_info("Tokens generados:")
                    for token in tokens:
                        mostrar_info(str(token))
                    continue
                elif linea == "sugerencias":
                    for s in get_suggestions():
                        mostrar_info(str(s))
                    continue
                elif linea == "ast":
                    tokens = Lexer(linea).tokenizar()
                    ast = Parser(tokens).parsear()
                    try:
                        for nodo in ast:
                            if validador is not None:
                                nodo.aceptar(validador)
                    except PrimitivaPeligrosaError as pe:
                        logging.error(f"Primitiva peligrosa: {pe}")
                        print(f"Error: {pe}")
                        continue
                    mostrar_info("AST generado:")
                    mostrar_info(str(ast))
                    continue
                elif linea:
                    if sandbox:
                        try:
                            salida = ejecutar_en_sandbox(linea)
                            if salida:
                                mostrar_info(str(salida))
                        except Exception as e:
                            logging.error(f"Error en sandbox: {e}")
                            mostrar_error(f"Error en sandbox: {e}")
                        continue

                    tokens = Lexer(linea).tokenizar()
                    logging.debug(f"Tokens generados: {tokens}")
                    ast = Parser(tokens).parsear()
                    logging.debug(f"AST generado: {ast}")
                    try:
                        for nodo in ast:
                            if validador is not None:
                                nodo.aceptar(validador)
                    except PrimitivaPeligrosaError as pe:
                        logging.error(f"Primitiva peligrosa: {pe}")
                        mostrar_error(str(pe))
                        continue
                    interpretador.ejecutar_ast(ast)
            except SyntaxError as se:
                logging.error(f"Error de sintaxis: {se}")
                mostrar_error(f"Error procesando la entrada: {se}")
            except RuntimeError as re:
                logging.error(f"Error crítico: {re}")
                mostrar_error(f"Error crítico: {re}")
            except Exception as e:
                logging.error(f"Error general procesando la entrada: {e}")
                mostrar_error(f"Error procesando la entrada: {e}")
        return 0
