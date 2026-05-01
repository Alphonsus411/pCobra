import logging
import os
import re
import sys
import warnings
from typing import Optional, Any
from types import TracebackType

try:  # pragma: no cover - dependencia opcional
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
    PROMPT_TOOLKIT_AVAILABLE = True
except ModuleNotFoundError:  # pragma: no cover - entornos sin prompt_toolkit
    PromptSession = None  # type: ignore[assignment]
    PygmentsLexer = None  # type: ignore[assignment]
    FileHistory = None  # type: ignore[assignment]
    DummyOutput = None  # type: ignore[assignment]

    class NoConsoleScreenBufferError(Exception):
        """Excepción usada como marcador cuando falta prompt_toolkit."""

        pass

    PROMPT_TOOLKIT_AVAILABLE = False

from pcobra.cobra.core import Lexer, LexerError, TipoToken, UnclosedStringError
from pcobra.cobra.core import ParserError
from pcobra.cobra.cli.execution_pipeline import (
    construir_script_sandbox_canonico,
    prevalidar_y_parsear_codigo,
    resolver_interpretador_cls,
    validar_ast_seguro,
)
from pcobra.cobra.core import (
    NodoBucleMientras,
    NodoCondicional,
    NodoPara,
    NodoSwitch,
    NodoTryCatch,
)
from pcobra.cobra.core.runtime import (
    InterpretadorCobra,
    ejecutar_en_contenedor,
    ejecutar_en_sandbox,
    limitar_memoria_mb,
    PrimitivaPeligrosaError,
    validar_dependencias,
)
from pcobra.cobra.cli.commands.base import BaseCommand
from pcobra.cobra.cli.i18n import _, format_traceback
from pcobra.cobra.cli.utils.argument_parser import CustomArgumentParser
from pcobra.cobra.cli.utils.messages import (
    color_disabled,
    mostrar_advertencia,
    mostrar_error,
    mostrar_info,
)
from pcobra.cobra.cli.utils.parser_error_classifier import (
    es_parser_error_de_bloque_incompleto,
)
from pcobra.cobra.cli.utils.unicode_sanitize import sanitize_input
from pcobra.cobra.cli.repl.cobra_lexer import CobraLexer
from pcobra.cobra.cli.target_policies import (
    DOCKER_EXECUTABLE_TARGETS,
    DOCKER_RUNTIME_BY_TARGET,
    OFFICIAL_RUNTIME_TARGETS_HELP,
    build_runtime_capability_message,
    parse_runtime_target,
    resolve_docker_backend,
)
from pcobra.cobra.cli.transpiler_registry import cli_toml_map
DOCKER_RUNTIME_TARGETS = tuple(DOCKER_RUNTIME_BY_TARGET.values())
SANDBOX_DOCKER_CHOICES = DOCKER_EXECUTABLE_TARGETS
SANDBOX_DOCKER_HELP = OFFICIAL_RUNTIME_TARGETS_HELP

sys.modules.setdefault("cli.commands.interactive_cmd", sys.modules[__name__])


def _contains_isolated_surrogate(text: str) -> bool:
    """Detecta si aún hay code points surrogate en la cadena."""
    return any(0xD800 <= ord(ch) <= 0xDFFF for ch in text)


def _debug_assert_boundary_text_sanitized(text: str, *, context: str) -> None:
    """Aserción ligera de frontera para detectar surrogates aislados remanentes."""
    if __debug__:
        assert not _contains_isolated_surrogate(text), (
            f"Entrada Unicode no saneada en frontera ({context}); "
            "debe pasar por sanitize_input antes de validar/dispatch."
        )


def format_user_error(exc: Exception) -> str:
    """Normaliza mensajes de error para salida limpia en la CLI."""
    msg = " ".join(str(exc).strip().split())
    prefijos_redundantes = re.compile(
        r"^(?:error\s+general|error\s+cr[ií]tico|error\s+de\s+sintaxis|error)\s*[:：\-–—]?\s*",
        re.IGNORECASE,
    )

    while msg:
        limpio = prefijos_redundantes.sub("", msg, count=1)
        if limpio == msg:
            break
        msg = " ".join(limpio.split())

    return msg or _("Error desconocido")


class _SessionHistoryFallback:
    """Historial mínimo para dobles de sesión usados en pruebas."""

    def __init__(self, path: str) -> None:
        self._path = path

    def append_string(self, value: object) -> None:
        if isinstance(value, str):
            raw_value = value
        elif value is None:
            raw_value = ""
        else:
            raw_value = str(value)

        sanitized = sanitize_input(raw_value)
        _debug_assert_boundary_text_sanitized(
            sanitized,
            context="_SessionHistoryFallback.append_string",
        )
        with open(self._path, "a", encoding="utf-8") as fh:
            fh.write(f"{sanitized}\n")

if FileHistory is not None:
    class SafeFileHistory(FileHistory):
        """Historial endurecido que sanitiza entradas antes de persistir."""

        def append_string(self, value: object) -> None:
            if isinstance(value, str):
                raw_value = value
            elif value is None:
                raw_value = ""
            else:
                raw_value = str(value)

            sanitized = sanitize_input(raw_value)
            _debug_assert_boundary_text_sanitized(
                sanitized,
                context="SafeFileHistory.append_string",
            )
            super().append_string(sanitized)

else:
    SafeFileHistory = None  # type: ignore[assignment]


class InteractiveCommand(BaseCommand):
    """Modo interactivo del lenguaje Cobra.

    Esta clase implementa un REPL (Read-Eval-Print Loop) para el lenguaje Cobra,
    permitiendo la ejecución interactiva de código con diferentes modos de
    ejecución (normal, sandbox, contenedor Docker).
    """

    name = "interactive"
    requires_sqlite_key: bool = False
    MAX_LINE_LENGTH = 10000
    MEMORY_LIMIT_MB = 1024
    MAX_AST_DEPTH = 100
    MAX_LINEAS_BLANCO_CONSECUTIVAS_EN_BLOQUE = 2
    ERROR_FIN_SIN_BLOQUE = _("'fin' sin bloque abierto.")
    ERROR_BLOQUE_VACIO = _(
        "El bloque no puede cerrarse con 'fin' sin sentencias no vacías."
    )
    ERROR_EXCESO_LINEAS_BLANCO = _(
        "Máximo de {maximo} líneas en blanco consecutivas dentro de un bloque."
    )
    _TOKENS_APERTURA_BLOQUE = frozenset(
        {
            TipoToken.SI,
            TipoToken.MIENTRAS,
            TipoToken.PARA,
            TipoToken.FUNC,
            TipoToken.CLASE,
            TipoToken.TRY,
            TipoToken.INTENTAR,
            TipoToken.SWITCH,
        }
    )
    _NODOS_CONTROL_SIN_ECHO_REPL = (
        NodoCondicional,
        NodoBucleMientras,
        NodoPara,
        NodoTryCatch,
        NodoSwitch,
    )
    _NOMBRES_NODOS_CONTROL_SIN_ECHO_REPL = frozenset(
        {
            "NodoCondicional",
            "NodoBucleMientras",
            "NodoSi",
            "NodoMientras",
            "NodoPara",
            "NodoTryCatch",
            "NodoSwitch",
        }
    )

    def __init__(self, interpretador: InterpretadorCobra) -> None:
        """Inicializa el comando interactivo.

        Args:
            interpretador: Instancia del intérprete de Cobra
        """
        super().__init__()
        self.interpretador = interpretador
        self._allow_insecure_fallback = False
        # Contrato de logging: no agregar handlers por comando; la emisión se
        # centraliza en root configurado desde ``pcobra.cli.configure_logging``.
        self.logger = logging.getLogger(__name__)
        self._estado_repl = self._crear_estado_repl()
        # Estado local para tracebacks técnicos en REPL.
        # Fuente canónica: flag global --debug parseado por la CLI principal.
        self._debug_mode = False
        self._seguro_repl = True
        self._extra_validators_repl: Any = None
        self._interpretador_sesion: Optional[InterpretadorCobra] = None
        self.mode = "analysis"

    @staticmethod
    def _crear_estado_repl() -> dict[str, Any]:
        """Crea el estado de sesión del REPL."""
        return {
            "buffer_lineas": [],
            "nivel_bloque": 0,
            "lineas_blanco_consecutivas": 0,
            "debug_enabled": False,
        }

    def register_subparser(self, subparsers: Any) -> CustomArgumentParser:
        """Registra los argumentos del subcomando.

        Args:
            subparsers: Objeto para registrar subcomandos

        Returns:
            Parser configurado para el subcomando
        """
        parser = subparsers.add_parser(
            self.name,
            help=_("Inicia el modo interactivo"),
            description=_(
                "REPL de Cobra. Dentro de bloques se permiten como máximo "
                "{maximo} líneas en blanco consecutivas y se prohíben bloques vacíos."
            ).format(maximo=self.MAX_LINEAS_BLANCO_CONSECUTIVAS_EN_BLOQUE),
        )
        parser.add_argument(
            "--sandbox",
            action="store_true",
            help=_("Ejecuta cada línea dentro de una sandbox"),
        )
        parser.add_argument(
            "--sandbox-docker",
            type=lambda value: parse_runtime_target(
                value,
                allowed_targets=SANDBOX_DOCKER_CHOICES,
                capability="modo interactivo con Docker",
            ),
            choices=SANDBOX_DOCKER_CHOICES,
            help=_(
                "Target con runtime Docker oficial para modo interactivo "
                "({targets}). El REPL solo ejecuta runtimes oficiales reales, "
                "no cualquier target oficial de salida. {policy}"
            ).format(
                targets=SANDBOX_DOCKER_HELP,
                policy=build_runtime_capability_message(
                    capability="modo interactivo con Docker",
                    allowed_targets=SANDBOX_DOCKER_CHOICES,
                ),
            ),
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

        # Rechazar solo caracteres de control no imprimibles
        if re.search(r"[\x00-\x08\x0b\x0c\x0e-\x1f]", linea):
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

        ast = prevalidar_y_parsear_codigo(linea)
        self.logger.debug(_("AST generado: {ast}").format(ast=ast))

        self._validar_ast_para_analisis(ast, validador)

        return ast


    def _recorrer_validacion_ast(
        self,
        ast: list[Any],
        validador: Optional[Any],
        *,
        silencioso: bool,
    ) -> None:
        """Recorre el AST con el validador opcional y política explícita de efectos."""
        if not validador:
            return

        def _visitar() -> None:
            for nodo in ast:
                nodo.aceptar(validador)

        if not silencioso:
            _visitar()
            return

        verbose_prev = getattr(validador, "verbose", None)
        if verbose_prev is not None:
            try:
                setattr(validador, "verbose", False)
            except Exception:
                verbose_prev = None

        emitir_prev = getattr(validador, "emitir_side_effects", None)
        if emitir_prev is not None:
            try:
                setattr(validador, "emitir_side_effects", False)
            except Exception:
                emitir_prev = None

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            _visitar()

        if verbose_prev is not None:
            try:
                setattr(validador, "verbose", verbose_prev)
            except Exception:
                pass

        if emitir_prev is not None:
            try:
                setattr(validador, "emitir_side_effects", emitir_prev)
            except Exception:
                pass

    def _validar_ast_para_analisis(self, ast: list[Any], validador: Optional[Any]) -> None:
        """Valida AST para análisis estático sin side effects observables."""
        self._recorrer_validacion_ast(ast, validador, silencioso=True)

    def _validar_ast_para_ejecucion(self, ast: list[Any], validador: Optional[Any]) -> None:
        """Valida AST para ejecución con side effects de auditoría habilitados."""
        self._recorrer_validacion_ast(ast, validador, silencioso=False)

    def _ejecutar_ast_en_repl(
        self,
        ast: list[Any],
        validador: Optional[Any] = None,
        *,
        validar_no_silencioso: bool = True,
    ) -> tuple[list[Any], Any]:
        """Flujo canónico del REPL incremental.

        Contrato: REPL incremental = intérprete; no batch pipeline.
        Patrón explícito del flujo normal:
        1) ``ast = prevalidar_y_parsear_codigo(codigo)``;
        2) validación de seguridad/validadores de ejecución (fase de ejecución);
        3) ``for nodo in ast: self.interpretador.ejecutar_nodo(nodo)``.

        Invariantes de fase (antirregresión):
        - La fase de análisis usa ``_validar_ast_para_analisis`` (silenciosa,
          sin side effects observables de auditoría).
        - La fase de ejecución usa ``_validar_ast_para_ejecucion`` (con side
          effects de auditoría cuando aplica).
        - Para un mismo propósito de logging/auditoría, no mezclar ambas fases
          sobre el mismo AST en una única corrida de ejecución.

        Nota de mantenimiento:
        Los nombres temporales ``_cse*`` pertenecen a optimizaciones internas
        de pipelines batch/backend y no deben filtrarse al flujo normal del REPL.
        Aquí se evalúan nodos AST ya parseados directamente sobre el entorno
        actual del intérprete de sesión.
        """

        # Contrato: REPL incremental = intérprete; no batch pipeline.
        if self._seguro_repl:
            validar_ast_seguro(
                ast,
                validadores_extra=self._extra_validators_repl,
            )
        resultado = None
        if validar_no_silencioso:
            self._validar_ast_para_ejecucion(ast, validador)

        for nodo in ast:
            resultado_nodo = self.interpretador.ejecutar_nodo(nodo)
            # El resultado observable del REPL debe ser el valor realmente
            # evaluado por el último nodo ejecutado en el entorno actual.
            resultado = resultado_nodo
        return ast, resultado

    def ejecutar_codigo(
        self,
        codigo: str,
        validador: Optional[Any] = None,
        *,
        ast_preparseado: Optional[list[Any]] = None,
    ) -> None:
        """Ejecuta un snippet en modo REPL incremental.

        Contrato: REPL incremental = intérprete; no batch pipeline.
        Cada entrada se evalúa sobre ``self.interpretador`` (estado acumulado),
        no como una compilación por lotes/batch aislada.
        """

        self.logger.debug("[RUN] Ejecutando snippet en REPL")
        self._sincronizar_interpretador_sesion()
        # REPL = intérprete incremental (estado acumulado en self.interpretador).
        # Contrato REPL (normal): no usar ``ejecutar_pipeline_explicito`` aquí.
        # Este camino ejecuta snippets interactivos normales sobre el intérprete
        # persistente para preservar la semántica incremental del lenguaje.
        modo_previo = self.mode
        validacion_no_silenciosa_realizada = False
        try:
            ast = ast_preparseado if ast_preparseado is not None else prevalidar_y_parsear_codigo(codigo)
            # Si no viene AST preparseado, esta fase sigue siendo de análisis
            # (sin emisión); la ejecución con emisión se habilita únicamente
            # dentro de ``_ejecutar_ast_en_repl``.
            if ast_preparseado is None:
                self.mode = "analysis"
                self.interpretador.mode = self.mode
                self._validar_ast_para_analisis(ast, validador)
            self.mode = "execution"
            self.interpretador.mode = self.mode
            ast, resultado = self._ejecutar_ast_en_repl(
                ast,
                validador,
                validar_no_silencioso=True,
            )
            validacion_no_silenciosa_realizada = True
        except Exception as err_original:
            if not self._debe_intentar_fallback_expresion_top_level(
                codigo, err_original, validador
            ):
                raise

            codigo_fallback = f"imprimir({codigo.strip()})"
            try:
                ast_fallback = prevalidar_y_parsear_codigo(codigo_fallback)
                self.mode = "execution"
                self.interpretador.mode = self.mode
                ast, resultado = self._ejecutar_ast_en_repl(
                    ast_fallback,
                    validador,
                    validar_no_silencioso=not validacion_no_silenciosa_realizada,
                )
            except Exception as err_fallback:
                if self._debe_intentar_fallback_expresion_top_level(
                    codigo, err_fallback, validador
                ):
                    raise err_original
                raise
        finally:
            # Restaurar modo previo evita contaminar evaluaciones siguientes del REPL
            # y mantiene aislada la transición análisis -> ejecución de este snippet.
            self.mode = modo_previo
            self.interpretador.mode = self.mode
        self.logger.debug("[EXEC] Ejecutando AST en intérprete")
        self.logger.debug("[EVAL] Resultado de evaluación: %r", resultado)
        self._imprimir_resultado_repl(ast, resultado)

    def parsear_y_ejecutar_codigo_repl(
        self,
        codigo: str,
        validador: Optional[Any] = None,
        *,
        prevalidar_fn: Any = prevalidar_y_parsear_codigo,
    ) -> None:
        """Valida sintaxis y delega la ejecución REPL al intérprete.

        Contrato: REPL incremental = intérprete; no batch pipeline.
        Este helper del flujo normal solo debe hacer:
        1) prevalidación/parseo;
        2) delegación a ``ejecutar_codigo``.

        Nota técnica (doble pasada REPL):
        - Pasada 1 (análisis): parseo + ``_validar_ast_para_analisis`` sin
          side effects observables.
        - Pasada 2 (ejecución): ``_validar_ast_para_ejecucion`` + evaluación
          real nodo a nodo en ``self.interpretador``.
        """

        self._sincronizar_interpretador_sesion()
        ast = prevalidar_fn(codigo)
        # Contrato de prevalidación/parseo en REPL: esta fase es solo de
        # análisis y no debe emitir side effects de auditoría.
        self.mode = "analysis"
        self.interpretador.mode = self.mode
        self._validar_ast_para_analisis(ast, validador)
        # Contrato de dispatch:
        # REPL = intérprete incremental; pipeline explícito solo para sandbox/setup.
        # Este helper delega en ``ejecutar_codigo`` y, por diseño, no debe
        # introducir pipeline explícito para snippets normales.
        # Invariante antirregresión: conservar este método como "thin wrapper"
        # (prevalidar + delegar a ejecutar_codigo) sin rutas batch adicionales.
        self.ejecutar_codigo(codigo, validador, ast_preparseado=ast)

    def _debe_intentar_fallback_expresion_top_level(
        self,
        codigo: str,
        err_original: Exception,
        validador: Optional[Any] = None,
    ) -> bool:
        """Determina si aplica fallback a ``imprimir(...)`` para expresiones top-level."""

        mensaje_error = str(err_original)
        if "Nodo no soportado" not in mensaje_error or "Nodo" not in mensaje_error:
            return False

        ast = prevalidar_y_parsear_codigo(codigo)
        # Ruta de análisis para decidir fallback: validar en modo silencioso
        # para evitar auditoría ruidosa antes de la ejecución real del AST.
        self._validar_ast_para_analisis(ast, validador)
        if not self._es_expresion_top_level_elegible(ast):
            return False

        if not self._es_consistente_nodo_error_vs_ast(
            mensaje_error=mensaje_error,
            ast=ast,
        ):
            return False

        return True

    def _es_expresion_top_level_elegible(self, ast: list[Any]) -> bool:
        """Valida fallback de echo en REPL sin alterar semántica de statements normales.

        Este helper existe para que `imprimir(...)` solo se inyecte cuando el AST
        represente una expresión top-level elegible, evitando transformar
        sentencias de control/declaración.
        """
        if len(ast) != 1:
            return False

        nodo = ast[0]
        nombre_nodo = nodo.__class__.__name__
        if not nombre_nodo.startswith("Nodo"):
            return False

        nodos_no_expresion = frozenset(
            {
                "NodoAsignacion",
                "NodoImprimir",
                "NodoCondicional",
                "NodoBucleMientras",
                "NodoMientras",
                "NodoPara",
                "NodoFor",
                "NodoFuncion",
                "NodoClase",
                "NodoRetorno",
                "NodoImport",
                "NodoUsar",
                "NodoTryCatch",
                "NodoThrow",
                "NodoAssert",
                "NodoDel",
                "NodoGlobal",
                "NodoNoLocal",
                "NodoWith",
                "NodoHolobit",
                "NodoHilo",
                "NodoRomper",
                "NodoContinuar",
                "NodoEsperar",
                "NodoSwitch",
            }
        )
        if nombre_nodo in nodos_no_expresion:
            return False

        nodos_expresion_permitidos = frozenset(
            {
                "NodoOperacionBinaria",
                "NodoOperacionUnaria",
                "NodoLlamadaFuncion",
                "NodoIdentificador",
                "NodoValor",
            }
        )
        if nombre_nodo in nodos_expresion_permitidos:
            return True

        return nombre_nodo.startswith("Nodo")

    def _es_consistente_nodo_error_vs_ast(
        self,
        *,
        mensaje_error: str,
        ast: list[Any],
        validar_consistencia: bool = True,
    ) -> bool:
        """Verifica consistencia opcional entre nodo reportado en error y AST real."""
        if not validar_consistencia:
            return True
        if len(ast) != 1:
            return False

        match_nodo = re.search(r"(Nodo[A-Za-z0-9_]+)", mensaje_error)
        if not match_nodo:
            return True

        nombre_nodo_ast = ast[0].__class__.__name__
        return match_nodo.group(1) == nombre_nodo_ast

    def _imprimir_resultado_repl(self, ast: list[Any], resultado: Any) -> None:
        """Imprime el resultado del REPL cuando aplica contrato de echo."""

        debe_imprimir_resultado = (
            resultado is not None
            and len(ast) == 1
            and ast[0].__class__.__name__ not in {"NodoImprimir", "NodoAsignacion"}
            and not self._es_nodo_control_sin_echo_repl(ast[0])
        )
        if debe_imprimir_resultado:
            if isinstance(resultado, bool):
                print("verdadero" if resultado else "falso")
            else:
                print(resultado)

    def _es_nodo_control_sin_echo_repl(self, nodo: Any) -> bool:
        """Determina si un nodo de control debe omitir echo de resultado en REPL."""

        return isinstance(nodo, self._NODOS_CONTROL_SIN_ECHO_REPL) or (
            nodo.__class__.__name__ in self._NOMBRES_NODOS_CONTROL_SIN_ECHO_REPL
        )

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
            validar_dependencias("python", cli_toml_map())
        except (ValueError, FileNotFoundError) as err:
            mostrar_error(
                _("Error de dependencias durante la inicialización: {err}").format(
                    err=err
                )
            )
            return 1

        self._debug_mode = bool(getattr(args, "debug", False))
        self._estado_repl["debug_enabled"] = self._debug_mode

        # Configurar modo seguro y validadores para el flujo AST canónico del REPL.
        self._seguro_repl = bool(getattr(args, "seguro", True))
        self._extra_validators_repl = getattr(args, "extra_validators", None)

        # Obtener modos de ejecución
        sandbox = getattr(args, "sandbox", False)
        sandbox_docker = getattr(args, "sandbox_docker", None)
        self._allow_insecure_fallback = bool(getattr(args, "allow_insecure_fallback", False))
        if sandbox_docker and sandbox_docker not in DOCKER_EXECUTABLE_TARGETS:
            mostrar_error(
                build_runtime_capability_message(
                    capability="modo interactivo con Docker",
                    allowed_targets=DOCKER_EXECUTABLE_TARGETS,
                )
            )
            return 1
        if not PROMPT_TOOLKIT_AVAILABLE:
            mostrar_advertencia(
                _(
                    "'prompt_toolkit' no está disponible; se activará un REPL básico sin autocompletado."
                )
            )
            return self._run_repl_basico(args, validador=None)
        history_path = os.path.expanduser("~/.cobra_history")
        os.makedirs(os.path.dirname(history_path), exist_ok=True)
        try:
            session = PromptSession(
                lexer=PygmentsLexer(CobraLexer),
                history=self._construir_historial(history_path),
            )
        except NoConsoleScreenBufferError:
            mostrar_advertencia(
                _(
                    "Entorno sin consola compatible, usando salida simplificada."
                )
            )
            session = PromptSession(
                lexer=PygmentsLexer(CobraLexer),
                history=self._construir_historial(history_path),
                output=DummyOutput(),
            )
        if not hasattr(session, "history"):
            # Compatibilidad con dobles de pruebas que no propagan ``history``.
            session.history = _SessionHistoryFallback(history_path)  # type: ignore[attr-defined]

        with self:
            self._run_repl_loop(
                args=args,
                validador=None,
                leer_linea=session.prompt,
                sandbox=sandbox,
                sandbox_docker=sandbox_docker,
            )

        return 0

    def _run_repl_basico(self, args: Any, validador: Optional[Any] = None) -> int:
        """Ejecuta un bucle REPL simplificado sin ``prompt_toolkit``."""

        sandbox = getattr(args, "sandbox", False)
        sandbox_docker = getattr(args, "sandbox_docker", None)
        if sandbox_docker:
            mostrar_error(
                _(
                    "El REPL básico no soporta la opción --sandbox-docker sin 'prompt_toolkit'."
                )
            )
            return 1

        with self:
            self._run_repl_loop(
                args=args,
                validador=None,
                leer_linea=input,
                sandbox=sandbox,
                sandbox_docker=None,
            )

        return 0

    def _run_repl_loop(
        self,
        args: Any,
        validador: Optional[Any],
        leer_linea: Any,
        sandbox: bool,
        sandbox_docker: Optional[str],
    ) -> None:
        """Bucle único de REPL para evitar divergencias entre implementaciones."""
        estado = self._crear_estado_repl()
        estado["debug_enabled"] = self._debug_mode
        estado["fase"] = "analisis"
        self._estado_repl = estado
        self._interpretador_sesion = self.interpretador
        while True:
            try:
                prompt = "... " if estado["buffer_lineas"] else ">>> "
                raw_linea = leer_linea(prompt)
                linea = sanitize_input(raw_linea if isinstance(raw_linea, str) else str(raw_linea))
                linea = linea.strip()
                _debug_assert_boundary_text_sanitized(
                    linea,
                    context="InteractiveCommand._run_repl_loop:pre-validacion",
                )
            except (KeyboardInterrupt, EOFError):
                if estado["buffer_lineas"]:
                    mostrar_error(_("Bloque incompleto; se limpiará la entrada actual."))
                    self._limpiar_estado_repl(estado)
                    continue
                mostrar_info(_("Saliendo..."))
                break

            if not linea:
                try:
                    self._manejar_linea_blanca(estado)
                except ParserError as err:
                    self._log_error(_("Error de sintaxis"), err)
                continue

            linea = sanitize_input(linea)
            _debug_assert_boundary_text_sanitized(
                linea,
                context="InteractiveCommand._run_repl_loop:pre-lexer-parser",
            )
            if not self.validar_entrada(linea):
                continue

            if not estado["buffer_lineas"] and linea in ["salir", "salir()"]:
                break

            if not estado["buffer_lineas"] and self._procesar_comando_especial(
                linea, validador
            ):
                continue

            try:
                estado["buffer_lineas"].append(linea)
                codigo = "\n".join(estado["buffer_lineas"])
                estado["fase"] = "analisis"
                ast = self.procesar_ast(codigo, validador)
                estado["lineas_blanco_consecutivas"] = 0
            except (LexerError, ParserError) as err:
                if self._es_error_de_bloque_incompleto(err):
                    continue
                estado["buffer_lineas"].clear()
                estado["lineas_blanco_consecutivas"] = 0
                categoria = self._clasificar_error_repl(err)
                self._log_error(categoria, err)
                continue
            except Exception as err:  # pragma: no cover - ruta unificada de errores
                estado["buffer_lineas"].clear()
                estado["lineas_blanco_consecutivas"] = 0
                categoria = self._clasificar_error_repl(err)
                self._log_error(categoria, err)
                continue

            try:
                codigo = sanitize_input(codigo)
                _debug_assert_boundary_text_sanitized(
                    codigo,
                    context="InteractiveCommand._run_repl_loop:pre-dispatch",
                )

                if sandbox:
                    self._ejecutar_en_sandbox(codigo)
                elif sandbox_docker:
                    self._ejecutar_en_docker(codigo, sandbox_docker)
                else:
                    estado["fase"] = "ejecucion"
                    # Contrato de dispatch:
                    # REPL = intérprete incremental; pipeline explícito solo para sandbox/setup.
                    # Rama normal: AST directo con entorno persistente.
                    self.ejecutar_codigo(codigo, validador, ast_preparseado=ast)
                estado["buffer_lineas"].clear()
                estado["fase"] = "analisis"
            except Exception as err:  # pragma: no cover - ruta unificada de errores
                estado["buffer_lineas"].clear()
                estado["fase"] = "analisis"
                categoria = self._clasificar_error_repl(err)
                self._log_error(categoria, err)

    def _sincronizar_interpretador_sesion(self) -> None:
        """Garantiza que el REPL use la misma instancia de intérprete por sesión."""

        if self._interpretador_sesion is None:
            self._interpretador_sesion = self.interpretador
            return
        if self.interpretador is not self._interpretador_sesion:
            self.interpretador = self._interpretador_sesion

    def _clasificar_error_repl(self, error: Exception) -> str:
        """Clasifica errores del REPL para un reporte único en el loop principal."""
        if isinstance(error, (LexerError, ParserError)):
            return _("Error de sintaxis")
        if isinstance(error, RuntimeError):
            return _("Error crítico")
        return _("Error general")

    def _limpiar_estado_repl(self, estado: dict[str, Any]) -> None:
        estado["buffer_lineas"].clear()
        estado["nivel_bloque"] = 0
        estado["lineas_blanco_consecutivas"] = 0

    def _manejar_linea_blanca(self, estado: dict[str, Any]) -> None:
        """Aplica política de líneas en blanco en sesión REPL."""
        if estado["buffer_lineas"]:
            estado["lineas_blanco_consecutivas"] += 1
            if (
                estado["lineas_blanco_consecutivas"]
                > self.MAX_LINEAS_BLANCO_CONSECUTIVAS_EN_BLOQUE
            ):
                raise ParserError(
                    self.ERROR_EXCESO_LINEAS_BLANCO.format(
                        maximo=self.MAX_LINEAS_BLANCO_CONSECUTIVAS_EN_BLOQUE
                    )
                )
        else:
            estado["lineas_blanco_consecutivas"] = 0

    def _es_error_de_bloque_incompleto(self, exc: Exception) -> bool:
        """Determina si el parser reportó una entrada todavía incompleta."""
        return es_parser_error_de_bloque_incompleto(exc)

    def _bloque_con_solo_lineas_vacias(self, buffer_lineas: list[str]) -> bool:
        """Indica si el bloque actual no contiene sentencias no vacías."""
        if len(buffer_lineas) < 2:
            return True
        lineas_intermedias = buffer_lineas[1:-1]
        return all(not linea.strip() for linea in lineas_intermedias)

    def _actualizar_nivel_bloque_por_linea(self, linea: str) -> int:
        """Actualiza el contador de profundidad según la línea tokenizada."""
        if not linea.strip():
            return 0
        tokens = self._tokenizar_para_balance(linea)
        delta = 0
        for token in tokens:
            if token.tipo in self._TOKENS_APERTURA_BLOQUE:
                delta += 1
            elif token.tipo == TipoToken.FIN:
                delta -= 1
        return delta

    def _tokenizar_para_balance(self, codigo: str) -> list[Any]:
        """Tokeniza código para calcular balance estructural del bloque."""
        if not codigo.strip():
            return []
        return Lexer(codigo).tokenizar()

    def _contar_aperturas_bloque(self, codigo: str) -> int:
        """Cuenta aperturas de bloque ignorando cadenas y comentarios."""
        tokens = self._tokenizar_para_balance(codigo)
        return sum(1 for token in tokens if token.tipo in self._TOKENS_APERTURA_BLOQUE)

    def _contar_cierres_bloque(self, codigo: str) -> int:
        """Cuenta cierres de bloque mediante el token ``FIN``."""
        tokens = self._tokenizar_para_balance(codigo)
        return sum(1 for token in tokens if token.tipo == TipoToken.FIN)

    def _calcular_balance_estructural(self, codigo: str) -> int:
        """Calcula el balance estructural acumulado del buffer multilinea."""
        if not codigo.strip():
            return 0
        try:
            aperturas = self._contar_aperturas_bloque(codigo)
            cierres = self._contar_cierres_bloque(codigo)
        except UnclosedStringError:
            return 1
        return max(0, aperturas - cierres)

    def _actualizar_buffer_y_obtener_codigo_listo(
        self, buffer_lineas: list[str], linea: str
    ) -> Optional[str]:
        """Agrega línea al buffer y retorna código completo si el bloque cerró."""
        nivel_actual = int(self._estado_repl.get("nivel_bloque", 0))
        delta = self._actualizar_nivel_bloque_por_linea(linea)
        if nivel_actual == 0 and delta < 0:
            raise ParserError(self.ERROR_FIN_SIN_BLOQUE)

        buffer_lineas.append(linea)
        nuevo_nivel = max(0, nivel_actual + delta)
        self._estado_repl["nivel_bloque"] = nuevo_nivel
        self._estado_repl["lineas_blanco_consecutivas"] = 0

        if nuevo_nivel != 0:
            return None

        if linea.strip() == "fin" and self._bloque_con_solo_lineas_vacias(buffer_lineas):
            buffer_lineas.clear()
            raise ParserError(self.ERROR_BLOQUE_VACIO)

        codigo = "\n".join(buffer_lineas)
        buffer_lineas.clear()
        return codigo

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
            try:
                from pcobra.cobra.core.qualia_bridge import (
                    get_suggestions,  # optional subsystem
                )
            except (ImportError, ModuleNotFoundError):
                return True

            for s in get_suggestions():
                mostrar_info(str(s))
            return True

        if linea == "ast":
            try:
                ast = self.procesar_ast(linea, None)
                if self._seguro_repl:
                    validar_ast_seguro(
                        ast,
                        validadores_extra=self._extra_validators_repl,
                    )
                mostrar_info(_("AST generado:"))
                mostrar_info(str(ast))
            except PrimitivaPeligrosaError as err:
                self._log_error(_("Primitiva peligrosa"), err)
            return True

        return False

    def _ejecutar_pipeline_explicito_solo_setup_sandbox(self, interpretador_cls: type[Any]) -> Any:
        """Inicializa setup de sandbox con pipeline explícito (uso restringido).

        Contrato: este helper existe para aislar el único uso permitido de
        ``ejecutar_pipeline_explicito`` dentro del REPL: preparación de
        sandbox/setup. No debe reutilizarse para el flujo normal incremental.
        """
        from pcobra.cobra.cli.execution_pipeline import (
            ejecutar_pipeline_explicito,
            PipelineInput,
        )

        setup_input = PipelineInput(
            codigo="",
            interpretador_cls=interpretador_cls,
            safe_mode=self._seguro_repl,
            extra_validators=self._extra_validators_repl,
            interpretador=self.interpretador,
        )
        setup, _ = ejecutar_pipeline_explicito(
            setup_input,
            analizar_codigo_fn=lambda _codigo: [],
        )
        return setup

    def _ejecutar_en_sandbox(
        self,
        linea: str,
    ) -> None:
        """Ejecuta código en un sandbox.

        Args:
            linea: Código a ejecutar
        """
        interpretador_cls = resolver_interpretador_cls(
            module_name=__name__,
            default_cls=type(self.interpretador),
        )
        # REPL = intérprete incremental; pipeline explícito solo para sandbox/setup.
        # Contrato sandbox/setup: llamada encapsulada para evitar reutilización
        # accidental en flujo normal del REPL incremental.
        setup = self._ejecutar_pipeline_explicito_solo_setup_sandbox(interpretador_cls)
        self.interpretador = setup.interpretador
        self._seguro_repl = setup.safe_mode
        self._extra_validators_repl = setup.validadores_extra
        prevalidar_y_parsear_codigo(linea)

        script = construir_script_sandbox_canonico(
            linea,
            safe_mode=setup.safe_mode,
            extra_validators=setup.validadores_extra,
            imprimir_resultado=True,
        )

        salida = ejecutar_en_sandbox(
            script,
            allow_insecure_fallback=self._allow_insecure_fallback,
        )
        if salida:
            mostrar_info(str(salida))

    def _ejecutar_en_docker(self, linea: str, backend: str) -> None:
        """Ejecuta código en un contenedor Docker.

        Args:
            linea: Código a ejecutar
            backend: Backend a utilizar
        """
        backend_runtime = resolve_docker_backend(backend)
        salida = ejecutar_en_contenedor(linea, backend_runtime)
        if salida:
            mostrar_info(str(salida))

    def _log_error(self, categoria: str, error: Exception) -> None:
        """Registra y muestra un error.

        Args:
            categoria: Categoría técnica usada solo para logging interno
            error: Excepción ocurrida
        """
        mensaje_usuario = format_user_error(error)

        # Log técnico único (sin duplicar salida en consola del usuario).
        debug_enabled = bool(self._estado_repl.get("debug_enabled", self._debug_mode))
        logging.debug(
            "Error en REPL (%s): %s",
            categoria,
            mensaje_usuario,
            exc_info=debug_enabled,
        )

        with color_disabled():
            mostrar_error(mensaje_usuario, registrar_log=False)
        if debug_enabled:
            self.logger.debug(format_traceback(error))

    def __enter__(self) -> "InteractiveCommand":
        """Inicializa recursos del REPL.

        Returns:
            Self para uso en context manager
        """
        self.logger.debug(_("Iniciando REPL de Cobra"))
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
            self.logger.error(
                _("Error al finalizar REPL: {exc_val}").format(exc_val=exc_val)
            )
        self.logger.debug(_("Finalizando REPL de Cobra"))
    def _construir_historial(self, history_path: str) -> Any:
        if FileHistory is not None:
            return FileHistory(history_path)
        return _SessionHistoryFallback(history_path)
