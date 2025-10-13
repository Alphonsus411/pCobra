import logging
import os
import re
import traceback
from typing import Optional, Any
from types import TracebackType

from prompt_toolkit import PromptSession
from prompt_toolkit.lexers import PygmentsLexer
from prompt_toolkit.history import FileHistory
from prompt_toolkit.output import DummyOutput

try:
    from prompt_toolkit.output.win32 import NoConsoleScreenBufferError
except Exception:  # pragma: no cover - solo disponible en Windows
    class NoConsoleScreenBufferError(Exception):
        """Excepción usada cuando la consola no soporta buffer de pantalla."""
        pass

from pcobra.cobra.core import Lexer, LexerError
from pcobra.cobra.core import Parser, ParserError
from pcobra.cobra.transpilers import module_map
from pcobra.core.interpreter import InterpretadorCobra
from pcobra.core.resource_limits import limitar_memoria_mb
from pcobra.core.qualia_bridge import get_suggestions
from pcobra.core.sandbox import (
    ejecutar_en_contenedor,
    ejecutar_en_sandbox,
    validar_dependencias,
)
from pcobra.core.semantic_validators import PrimitivaPeligrosaError, construir_cadena
from pcobra.cobra.cli.commands.base import BaseCommand
from pcobra.cobra.cli.i18n import _
from pcobra.cobra.cli.utils.argument_parser import CustomArgumentParser
from pcobra.cobra.cli.utils.messages import (
    mostrar_advertencia,
    mostrar_error,
    mostrar_info,
)
from pcobra.cobra.cli.repl.cobra_lexer import CobraLexer


class InteractiveCommand(BaseCommand):
    """Modo interactivo del lenguaje Cobra.

    Esta clase implementa un REPL (Read-Eval-Print Loop) para el lenguaje Cobra,
    permitiendo la ejecución interactiva de código con diferentes modos de
    ejecución (normal, sandbox, contenedor Docker).
    """

    name = "interactive"
    MAX_LINE_LENGTH = 10000
    MEMORY_LIMIT_MB = 1024
    MAX_AST_DEPTH = 100

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
            level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
        )

    def register_subparser(self, subparsers: Any) -> CustomArgumentParser:
        """Registra los argumentos del subcomando.

        Args:
            subparsers: Objeto para registrar subcomandos

        Returns:
            Parser configurado para el subcomando
        """
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
        parser.add_argument(
            "--memory-limit",
            type=int,
            default=self.MEMORY_LIMIT_MB,
            help=_("Límite de memoria en MB"),
            metavar="MB",
        )
        parser.add_argument(
            "--ignore-memory-limit",
            action="store_true",
            help=_("Continúa aun si no se puede aplicar el límite de memoria"),
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

        # Validar caracteres especiales
        if re.search(r"[^\w\s\-\.\'\"]+", linea):
            mostrar_error(_("La entrada contiene caracteres no permitidos"))
            return False

        return True

    def procesar_ast(self, linea: str, validador: Optional[Any] = None, depth: int = 0):
        """Procesa una línea de código generando su AST.

        Args:
            linea: Código a procesar
            validador: Validador opcional para el AST
            depth: Profundidad actual del AST

        Returns:
            AST generado

        Raises:
            LexerError: Error durante el análisis léxico
            ParserError: Error durante el parsing
            PrimitivaPeligrosaError: Si se detecta una primitiva peligrosa
            RuntimeError: Si se excede la profundidad máxima permitida
        """
        if depth > self.MAX_AST_DEPTH:
            raise RuntimeError(_("Se excedió la profundidad máxima del AST"))

        tokens = Lexer(linea).tokenizar()
        logging.debug(_("Tokens generados: {tokens}").format(tokens=tokens))

        ast = Parser(tokens).parsear()
        logging.debug(_("AST generado: {ast}").format(ast=ast))

        if validador:
            for nodo in ast:
                nodo.aceptar(validador)

        return ast

    def run(self, args: Any) -> int:
        """Ejecuta el REPL de Cobra.

        Args:
            args: Argumentos del comando

        Returns:
            0 en caso de éxito, 1 en caso de error
        """
        try:
            # Validar y configurar límite de memoria
            memory_limit = getattr(args, "memory_limit", self.MEMORY_LIMIT_MB)
            ignore_memory_limit = getattr(args, "ignore_memory_limit", False)
            if memory_limit <= 0:
                mostrar_error(_("El límite de memoria debe ser positivo"))
                return 1

            try:
                limitar_memoria_mb(memory_limit)
            except NotImplementedError as e:
                mostrar_advertencia(
                    _("No se pudo aplicar el límite de memoria: {err}").format(err=e)
                )
            except RuntimeError as e:
                if ignore_memory_limit:
                    mostrar_advertencia(
                        _("No se pudo aplicar el límite de memoria: {err}").format(
                            err=e
                        )
                    )
                else:
                    mostrar_error(
                        _("Error al establecer límite de memoria: {err}").format(err=e)
                    )
                    return 1

            # Validar dependencias
            validar_dependencias("python", module_map.get_toml_map())
        except (ValueError, FileNotFoundError) as err:
            mostrar_error(
                _("Error de dependencias durante la inicialización: {err}").format(
                    err=err
                )
            )
            return 1

        # Configurar modo seguro y validadores
        seguro = getattr(args, "seguro", True)
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
        history_path = os.path.expanduser("~/.cobra_history")
        os.makedirs(os.path.dirname(history_path), exist_ok=True)
        try:
            session = PromptSession(
                lexer=PygmentsLexer(CobraLexer),
                history=FileHistory(history_path),
            )
        except NoConsoleScreenBufferError:
            mostrar_advertencia(
                _(
                    "Entorno sin consola compatible, usando salida simplificada."
                )
            )
            session = PromptSession(
                lexer=PygmentsLexer(CobraLexer),
                history=FileHistory(history_path),
                output=DummyOutput(),
            )

        with self:  # Usar context manager para recursos
            while True:
                try:
                    # Leer entrada
                    linea = session.prompt("cobra> ").strip()
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
                    mostrar_info(_("Saliendo..."))
                    break
                except (LexerError, ParserError) as err:
                    self._log_error(_("Error de sintaxis"), err)
                except RuntimeError as err:
                    self._log_error(_("Error crítico"), err)
                except Exception as err:
                    self._log_error(_("Error general"), err, include_traceback=True)

        return 0

    def _procesar_comando_especial(self, linea: str, validador: Optional[Any]) -> bool:
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
                self._log_error(_("Primitiva peligrosa"), err)
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
            self._log_error(_("Error en sandbox"), err)

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
            self._log_error(_("Error en contenedor Docker"), err)

    def _log_error(
        self, categoria: str, error: Exception, include_traceback: bool = False
    ) -> None:
        """Registra y muestra un error.

        Args:
            categoria: Categoría del error
            error: Excepción ocurrida
            include_traceback: Si se debe incluir la traza completa del error
        """
        mensaje = f"{categoria}: {error}"
        if include_traceback:
            mensaje += f"\n{traceback.format_exc()}"
        logging.error(mensaje)
        mostrar_error(mensaje)

    def __enter__(self) -> "InteractiveCommand":
        """Inicializa recursos del REPL.

        Returns:
            Self para uso en context manager
        """
        logging.info(_("Iniciando REPL de Cobra"))
        return self

    def __exit__(
        self,
        exc_type: Optional[type],
        exc_val: Optional[Exception],
        exc_tb: Optional[TracebackType],
    ) -> None:
        """Libera recursos del REPL.

        Args:
            exc_type: Tipo de la excepción si ocurrió alguna
            exc_val: Valor de la excepción
            exc_tb: Traceback de la excepción
        """
        if exc_type is not None:
            logging.error(
                _("Error al finalizar REPL: {exc_val}").format(exc_val=exc_val)
            )
        logging.info(_("Finalizando REPL de Cobra"))
