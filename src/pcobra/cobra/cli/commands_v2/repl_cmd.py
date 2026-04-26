from typing import Any

from pcobra.cobra.cli.commands.base import BaseCommand
from pcobra.cobra.cli.commands.interactive_cmd import (
    InteractiveCommand,
    SANDBOX_DOCKER_CHOICES,
)
from pcobra.cobra.cli.execution_pipeline import (
    prevalidar_y_parsear_codigo,
)
from pcobra.cobra.cli.i18n import _
from pcobra.cobra.cli.utils.parser_error_classifier import (
    _extraer_token_desde_error as extraer_token_desde_error_parser,
    es_parser_error_de_bloque_incompleto,
)
from pcobra.cobra.cli.utils.messages import mostrar_info
from pcobra.cobra.core import LexerError, ParserError
from pcobra.cobra.core.runtime import InterpretadorCobra
from pcobra.cobra.core.semantic_validators import PrimitivaPeligrosaError
from pcobra.cobra.cli.target_policies import parse_runtime_target
from pcobra.cobra.cli.utils.unicode_sanitize import sanitize_input

class ReplCommandV2(BaseCommand):
    """Comando v2 público para iniciar el REPL de Cobra."""
    # Nota técnica:
    # La semántica del camino normal (parseo + ejecución + fallback de
    # expresiones top-level) se define en InteractiveCommand.
    # ReplCommandV2 coordina IO/estado y delega ese contrato.

    name = "repl"
    capability = "execute"
    def __init__(self) -> None:
        super().__init__()
        self._delegate = InteractiveCommand(InterpretadorCobra())
        self._delegate.name = self.name
        # Mantener una única instancia viva para todo el ciclo de la sesión.
        self._interpretador_persistente: Any | None = self._delegate.interpretador
        self._seguro_repl: bool = True
        self._extra_validators_repl: Any = None

    def es_error_de_bloque_incompleto(self, exc: Exception) -> bool:
        """Delega la clasificación de entrada incompleta al clasificador central."""
        return es_parser_error_de_bloque_incompleto(exc)

    def _extraer_token_desde_error(self, err: Exception) -> Any | None:
        """Compatibilidad con pruebas históricas de extracción de token."""
        if not isinstance(err, ParserError):
            return None
        return extraer_token_desde_error_parser(err)

    def _manejar_error_prevalidacion(self, err: Exception, buffer: list[str]) -> None:
        """Procesa errores de prevalidación delegando la clasificación central."""
        if self.es_error_de_bloque_incompleto(err):
            return
        self._registrar_error_repl(err)
        self._reset_buffer_local(buffer)
        self._reset_estado_delegate()

    def register_subparser(self, subparsers: Any):
        parser = subparsers.add_parser(self.name, help=_("Start Cobra REPL"))
        parser.add_argument(
            "--sandbox",
            action="store_true",
            help=_("Execute each line in sandbox mode"),
        )
        parser.add_argument(
            "--sandbox-docker",
            type=lambda value: parse_runtime_target(
                value,
                allowed_targets=SANDBOX_DOCKER_CHOICES,
                capability="modo interactivo con Docker",
            ),
            choices=SANDBOX_DOCKER_CHOICES,
            help=_("Docker runtime target for REPL"),
        )
        parser.add_argument(
            "--memory-limit",
            type=int,
            default=self._delegate.MEMORY_LIMIT_MB,
            help=_("Memory limit in MB"),
            metavar="MB",
        )
        parser.add_argument(
            "--ignore-memory-limit",
            action="store_true",
            help=_("Continue even if memory limit cannot be applied"),
        )
        parser.set_defaults(cmd=self)
        return parser

    def _sincronizar_estado_hacia_delegate(self) -> None:
        """Sincroniza estado persistente local hacia el comando delegado."""
        # En modo normal siempre se reinyecta la misma referencia persistente
        # para evitar re-instanciación accidental entre snippets.
        if self._interpretador_persistente is not None:
            self._delegate.interpretador = self._interpretador_persistente
        self._delegate._seguro_repl = self._seguro_repl
        self._delegate._extra_validators_repl = self._extra_validators_repl

    def _sincronizar_estado_desde_delegate(self) -> None:
        """Sincroniza estado del comando delegado hacia el estado local."""
        if self._delegate.interpretador is not None:
            self._interpretador_persistente = self._delegate.interpretador
        self._seguro_repl = self._delegate._seguro_repl
        self._extra_validators_repl = self._delegate._extra_validators_repl

    def _ejecutar_en_modo_normal(
        self,
        codigo: str,
        interpretador_cls: type | None = None,
    ) -> None:
        """Ejecuta una entrada REPL reutilizando la lógica canónica de InteractiveCommand."""
        _ = interpretador_cls  # Compatibilidad con contratos de pruebas existentes.
        self._sincronizar_estado_hacia_delegate()
        try:
            self._delegate.parsear_y_ejecutar_codigo_repl(
                codigo,
                prevalidar_fn=prevalidar_y_parsear_codigo,
            )
        finally:
            self._sincronizar_estado_desde_delegate()

    def _registrar_error_repl(self, err: Exception) -> None:
        """Centraliza clasificación + visualización de errores REPL."""
        categoria = self._delegate._clasificar_error_repl(err)
        self._delegate._log_error(categoria, err)

    def _reset_buffer_local(self, buffer: list[str]) -> None:
        """Limpia el buffer de entrada local del REPL v2."""
        buffer.clear()

    def _reset_estado_delegate(self) -> None:
        """Restablece el estado base del REPL delegado.

        Solo limpia metadatos de captura/buffer del REPL y no toca el runtime
        (`interpretador`) para preservar contexto de variables.
        """
        self._delegate._estado_repl = self._delegate._crear_estado_repl()

    def run(self, args: Any) -> int:
        buffer: list[str] = []
        self._delegate._estado_repl = self._delegate._crear_estado_repl()
        self._seguro_repl = bool(getattr(args, "seguro", True))
        self._extra_validators_repl = getattr(args, "extra_validators", None)
        sandbox = bool(getattr(args, "sandbox", False))
        sandbox_docker = getattr(args, "sandbox_docker", None)

        while True:
            try:
                linea = input(">>> " if not buffer else "... ")
            except KeyboardInterrupt:
                if buffer:
                    mostrar_info(_("Entrada multilinea cancelada."))
                    self._reset_buffer_local(buffer)
                    self._reset_estado_delegate()
                    continue
                mostrar_info(_("Interrupción recibida. Saliendo del REPL."))
                break
            except EOFError:
                if buffer:
                    mostrar_info(_("Entrada multilinea cancelada por fin de archivo."))
                    self._reset_buffer_local(buffer)
                    self._reset_estado_delegate()
                    continue
                mostrar_info(_("Fin de entrada. Saliendo del REPL."))
                break

            linea = sanitize_input(linea)
            if not linea.strip():
                continue

            comando = linea.strip()
            if comando in {"salir", "exit"}:
                if buffer:
                    mostrar_info(_("Entrada multilinea cancelada. Saliendo del REPL."))
                    self._reset_buffer_local(buffer)
                    self._reset_estado_delegate()
                else:
                    mostrar_info(_("Saliendo..."))
                break

            buffer.append(linea)
            codigo = "\n".join(buffer)
            if sandbox or sandbox_docker:
                try:
                    prevalidar_y_parsear_codigo(codigo)
                except (LexerError, ParserError) as err:
                    if self.es_error_de_bloque_incompleto(err):
                        continue
                    self._registrar_error_repl(err)
                    self._reset_buffer_local(buffer)
                    self._reset_estado_delegate()
                    continue
                except Exception as err:
                    self._registrar_error_repl(err)
                    continue

            try:
                if sandbox:
                    self._delegate._ejecutar_en_sandbox(codigo)
                elif sandbox_docker:
                    self._delegate._ejecutar_en_docker(codigo, sandbox_docker)
                else:
                    self._ejecutar_en_modo_normal(codigo)
                self._reset_buffer_local(buffer)
                self._reset_estado_delegate()
            except (LexerError, ParserError) as err:
                if self.es_error_de_bloque_incompleto(err):
                    continue
                self._registrar_error_repl(err)
                self._reset_buffer_local(buffer)
                self._reset_estado_delegate()
                continue
            except (PrimitivaPeligrosaError, RuntimeError) as err:
                self._registrar_error_repl(err)
                self._reset_buffer_local(buffer)
                self._reset_estado_delegate()
                continue
            except Exception as err:
                self._registrar_error_repl(err)
                self._reset_buffer_local(buffer)
                self._reset_estado_delegate()
                continue

        return 0
