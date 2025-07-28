import logging

from cobra.lexico.lexer import Lexer
from cobra.parser.parser import Parser
from cobra.transpilers import module_map
from core.interpreter import InterpretadorCobra
from core.qualia_bridge import get_suggestions
from core.sandbox import (
    ejecutar_en_contenedor,
    ejecutar_en_sandbox,
    validar_dependencias,
)
from core.semantic_validators import PrimitivaPeligrosaError, construir_cadena

from cobra.cli.commands.base import BaseCommand
from cobra.cli.i18n import _
from cobra.cli.utils.messages import mostrar_error, mostrar_info


class InteractiveCommand(BaseCommand):
    """Modo interactivo del lenguaje Cobra."""

    name = "interactive"

    def __init__(self) -> None:
        super().__init__()
        # Intérprete reutilizable para mantener estado entre comandos
        self.interpretador = InterpretadorCobra()

    def register_subparser(self, subparsers):
        """Registra los argumentos del subcomando."""
        parser = subparsers.add_parser(self.name, help=_("Inicia el modo interactivo"))
        parser.add_argument(
            "--sandbox",
            action="store_true",
            help=_("Ejecuta cada línea dentro de una sandbox"),
        )
        parser.add_argument(
            "--sandbox-docker",
            choices=["python", "js", "cpp", "rust"],
            help=_("Ejecuta cada línea en un contenedor Docker"),
        )
        parser.set_defaults(cmd=self)
        return parser

    def run(self, args):
        """Ejecuta la lógica del comando."""
        seguro = getattr(args, "seguro", False)
        extra_validators = getattr(args, "validadores_extra", None)
        sandbox = getattr(args, "sandbox", False)
        sandbox_docker = getattr(args, "sandbox_docker", None)

        try:
            validar_dependencias("python", module_map.get_toml_map())
        except (ValueError, FileNotFoundError) as dep_err:
            mostrar_error(f"Error de dependencias: {dep_err}")
            return 1
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
                    mostrar_info(_("Tokens generados:"))
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
                        mostrar_error(str(pe))
                        continue
                    mostrar_info(_("AST generado:"))
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
                    if sandbox_docker:
                        try:
                            salida = ejecutar_en_contenedor(linea, sandbox_docker)
                            if salida:
                                mostrar_info(str(salida))
                        except Exception as e:
                            logging.error(f"Error en contenedor Docker: {e}")
                            mostrar_error(f"Error en contenedor Docker: {e}")
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
                    self.interpretador.ejecutar_ast(ast)
            except (KeyboardInterrupt, EOFError):
                mostrar_info("Saliendo...")
                break
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
