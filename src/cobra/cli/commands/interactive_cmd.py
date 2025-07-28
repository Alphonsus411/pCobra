import logging
import resource
from typing import Optional

from cobra.lexico.lexer import Lexer, LexerError
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


class ParserError:
    pass


class InteractiveCommand(BaseCommand):
    """Modo interactivo del lenguaje Cobra.
    
    Esta clase implementa un REPL (Read-Eval-Print Loop) para el lenguaje Cobra,
    permitiendo la ejecución interactiva de código con diferentes modos de
    ejecución (normal, sandbox, contenedor Docker).
    """

    name = "interactive"
    MAX_LINE_LENGTH = 10000
    MEMORY_LIMIT_MB = 1024

    def __init__(self, interpretador: InterpretadorCobra) -> None:
        """Inicializa el comando interactivo.

        Args:
            interpretador: Instancia del intérprete de Cobra
        """
        super().__init__()
        self.interpretador = interpretador
        self._setup_logging()

    def _setup_logging(self) -> None:
        """Configura el sistema de logging."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )

    def register_subparser(self, subparsers):
        """Registra los argumentos del subcomando.

        Args:
            subparsers: Objeto para registrar subcomandos
        
        Returns:
            Parser configurado para el subcomando
        """
        parser = subparsers.add_parser(
            self.name,
            help=_("Inicia el modo interactivo")
        )
        parser.add_argument(
            "--sandbox",
            action="store_true",
            help=_("Ejecuta cada línea dentro de una sandbox")
        )
        parser.add_argument(
            "--sandbox-docker",
            choices=["python", "js", "cpp", "rust"],
            help=_("Ejecuta cada línea en un contenedor Docker")
        )
        parser.add_argument(
            "--memory-limit",
            type=int,
            default=self.MEMORY_LIMIT_MB,
            help=_("Límite de memoria en MB")
        )
        parser.set_defaults(cmd=self)
        return parser

    def validar_entrada(self, linea: str) -> bool:
        """Valida la entrada del usuario.

        Args:
            linea: Línea de entrada a validar

        Returns:
            True si la entrada es válida, False en caso contrario
        """
        if not linea:
            return False
        if len(linea) > self.MAX_LINE_LENGTH:
            mostrar_error(_("Línea demasiado larga"))
            return False
        return True

    def procesar_ast(self, linea: str, validador: Optional[object] = None):
        """Procesa una línea de código generando su AST.

        Args:
            linea: Código a procesar
            validador: Validador opcional para el AST

        Returns:
            AST generado

        Raises:
            LexerError: Error durante el análisis léxico
            ParserError: Error durante el parsing
            PrimitivaPeligrosaError: Si se detecta una primitiva peligrosa
        """
        tokens = Lexer(linea).tokenizar()
        logging.debug(f"Tokens generados: {tokens}")
        
        ast = Parser(tokens).parsear()
        logging.debug(f"AST generado: {ast}")
        
        if validador:
            for nodo in ast:
                nodo.aceptar(validador)
        
        return ast

    def run(self, args):
        """Ejecuta el REPL de Cobra.

        Args:
            args: Argumentos del comando

        Returns:
            0 en caso de éxito, 1 en caso de error
        """
        try:
            # Configurar límite de memoria
            memory_limit = getattr(args, "memory_limit", self.MEMORY_LIMIT_MB)
            resource.setrlimit(
                resource.RLIMIT_AS,
                (memory_limit * 1024 * 1024,) * 2
            )

            # Validar dependencias
            validar_dependencias("python", module_map.get_toml_map())
        except (ValueError, FileNotFoundError) as err:
            mostrar_error(f"Error de inicialización: {err}")
            return 1

        # Configurar modo seguro y validadores
        seguro = getattr(args, "seguro", False)
        extra_validators = getattr(args, "validadores_extra", None)
        validador = None
        if seguro:
            validador = construir_cadena(
                InterpretadorCobra._cargar_validadores(extra_validators)
                if isinstance(extra_validators, str)
                else extra_validators
            )

        # Obtener modos de ejecución
        sandbox = getattr(args, "sandbox", False)
        sandbox_docker = getattr(args, "sandbox_docker", None)

        with self:  # Usar context manager para recursos
            while True:
                try:
                    # Leer entrada
                    linea = input("cobra> ").strip()
                    if not self.validar_entrada(linea):
                        continue

                    # Procesar comandos especiales
                    if linea in ["salir", "salir()"]:
                        break
                    
                    if self._procesar_comando_especial(linea, validador):
                        continue

                    # Ejecutar código
                    if sandbox:
                        self._ejecutar_en_sandbox(linea)
                    elif sandbox_docker:
                        self._ejecutar_en_docker(linea, sandbox_docker)
                    else:
                        ast = self.procesar_ast(linea, validador)
                        self.interpretador.ejecutar_ast(ast)

                except (KeyboardInterrupt, EOFError):
                    mostrar_info("Saliendo...")
                    break
                except (LexerError, ParserError) as err:
                    self._log_error(f"Error de sintaxis", err)
                except RuntimeError as err:
                    self._log_error("Error crítico", err)
                except Exception as err:
                    self._log_error("Error general", err)

        return 0

    def _procesar_comando_especial(self, linea: str, validador: Optional[object]) -> bool:
        """Procesa comandos especiales del REPL.

        Args:
            linea: Línea a procesar
            validador: Validador para el AST

        Returns:
            True si se procesó un comando especial, False en caso contrario
        """
        if linea == "tokens":
            tokens = Lexer(linea).tokenizar()
            mostrar_info(_("Tokens generados:"))
            for token in tokens:
                mostrar_info(str(token))
            return True

        if linea == "sugerencias":
            for s in get_suggestions():
                mostrar_info(str(s))
            return True

        if linea == "ast":
            try:
                ast = self.procesar_ast(linea, validador)
                mostrar_info(_("AST generado:"))
                mostrar_info(str(ast))
            except PrimitivaPeligrosaError as err:
                self._log_error("Primitiva peligrosa", err)
            return True

        return False

    def _ejecutar_en_sandbox(self, linea: str) -> None:
        """Ejecuta código en un sandbox.

        Args:
            linea: Código a ejecutar
        """
        try:
            salida = ejecutar_en_sandbox(linea)
            if salida:
                mostrar_info(str(salida))
        except Exception as err:
            self._log_error("Error en sandbox", err)

    def _ejecutar_en_docker(self, linea: str, backend: str) -> None:
        """Ejecuta código en un contenedor Docker.

        Args:
            linea: Código a ejecutar
            backend: Backend a utilizar
        """
        try:
            salida = ejecutar_en_contenedor(linea, backend)
            if salida:
                mostrar_info(str(salida))
        except Exception as err:
            self._log_error("Error en contenedor Docker", err)

    def _log_error(self, categoria: str, error: Exception) -> None:
        """Registra y muestra un error.

        Args:
            categoria: Categoría del error
            error: Excepción ocurrida
        """
        mensaje = f"{categoria}: {error}"
        logging.error(mensaje)
        mostrar_error(mensaje)

    def __enter__(self):
        """Inicializa recursos del REPL."""
        logging.info("Iniciando REPL de Cobra")
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Libera recursos del REPL."""
        logging.info("Finalizando REPL de Cobra")