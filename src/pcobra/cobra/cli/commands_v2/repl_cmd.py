from typing import Any

from pcobra.cobra.cli.commands.base import BaseCommand
from pcobra.cobra.cli.commands.interactive_cmd import (
    InteractiveCommand,
    SANDBOX_DOCKER_CHOICES,
)
from pcobra.cobra.cli.execution_pipeline import (
    PipelineInput,
    ejecutar_pipeline_explicito,
    prevalidar_y_parsear_codigo,
    resolver_interpretador_cls,
)
from pcobra.cobra.cli.i18n import _
from pcobra.cobra.cli.utils.messages import mostrar_info
from pcobra.cobra.core import LexerError, ParserError, TipoToken
from pcobra.cobra.core.runtime import InterpretadorCobra
from pcobra.cobra.core.semantic_validators import PrimitivaPeligrosaError
from pcobra.cobra.cli.target_policies import parse_runtime_target
from pcobra.cobra.cli.utils.unicode_sanitize import sanitize_input

_TOKENS_CIERRE_INCOMPLETO = {
    TipoToken.FIN,
    TipoToken.RPAREN,
    TipoToken.RBRACKET,
    TipoToken.RBRACE,
}


class ReplCommandV2(BaseCommand):
    """Comando v2 público para iniciar el REPL de Cobra."""

    name = "repl"
    capability = "execute"
    def __init__(self) -> None:
        super().__init__()
        self._delegate = InteractiveCommand(InterpretadorCobra())
        self._delegate.name = self.name
        self._interpretador_persistente: Any | None = None
        self._seguro_repl: bool = True
        self._extra_validators_repl: Any = None

    def _normalizar_tipo_token(self, valor: Any) -> TipoToken | None:
        """Normaliza posibles representaciones de token a ``TipoToken``."""
        if isinstance(valor, TipoToken):
            return valor
        if valor is None:
            return None
        nombre = str(valor).strip()
        if not nombre:
            return None
        if "." in nombre:
            nombre = nombre.split(".")[-1]
        try:
            return TipoToken[nombre]
        except KeyError:
            return None

    def _extraer_token_desde_error(self, err: ParserError) -> Any | None:
        """Obtiene el token actual desde metadatos del ``ParserError`` si existe."""
        for attr in (
            "token_actual",
            "token",
            "current_token",
            "actual_token",
            "last_token",
            "ultimo_token",
        ):
            if hasattr(err, attr):
                token = getattr(err, attr)
                if token is not None:
                    return token
        for attr in ("estado", "state", "parser_state"):
            if hasattr(err, attr):
                estado = getattr(err, attr)
                if estado is None:
                    continue
                for token_attr in ("token_actual", "token", "current_token"):
                    token = getattr(estado, token_attr, None)
                    if token is not None:
                        return token
        return None

    def _es_entrada_incompleta_por_metadata(self, err: ParserError) -> bool:
        """Determina incompleto **solo** con metadatos del ``ParserError``.

        El criterio es único y auditable: la entrada se considera incompleta
        únicamente cuando ``prevalidar_y_parsear_codigo`` emite un ``ParserError``
        que reporta EOF inesperado y, además, al menos un token de cierre
        pendiente en ``esperado`` (por ejemplo ``FIN``, ``RPAREN``,
        ``RBRACKET`` o ``RBRACE``).
        """
        token_actual = self._extraer_token_desde_error(err)
        tipo_token_actual = self._normalizar_tipo_token(
            getattr(token_actual, "tipo", None)
            if token_actual is not None
            else getattr(err, "tipo_token_actual", None)
            or getattr(err, "current_token_type", None)
        )

        esperado_raw = (
            getattr(err, "esperado", None)
            or getattr(err, "expected", None)
            or getattr(err, "tokens_esperados", None)
            or getattr(err, "expected_tokens", None)
            or getattr(err, "token_esperado", None)
            or getattr(err, "expected_token", None)
        )
        esperados = esperado_raw if isinstance(esperado_raw, (list, tuple, set)) else [esperado_raw]
        tipos_esperados = {self._normalizar_tipo_token(item) for item in esperados}
        tipos_esperados.discard(None)

        cierre_esperado = bool(tipos_esperados & _TOKENS_CIERRE_INCOMPLETO)
        if not cierre_esperado:
            return False

        eof_por_flag = bool(
            getattr(err, "unexpected_eof", False)
            or getattr(err, "eof", False)
            or getattr(err, "es_eof", False)
        )
        eof_por_token = tipo_token_actual == TipoToken.EOF
        return eof_por_flag or eof_por_token

    def es_error_de_bloque_incompleto(self, exc: Exception) -> bool:
        """Detecta si la excepción corresponde a una entrada aún incompleta.

        La decisión sale exclusivamente del ``ParserError`` emitido por
        ``prevalidar_y_parsear_codigo``: EOF inesperado + cierres pendientes
        en tokens esperados.
        """

        if not isinstance(exc, ParserError):
            return False
        return self._es_entrada_incompleta_por_metadata(exc)

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

    def _ejecutar_en_modo_normal(self, codigo: str, interpretador_cls: type) -> None:
        """Ejecuta una entrada REPL usando el pipeline CLI compartido."""
        setup, _resultado_pipeline = ejecutar_pipeline_explicito(
            PipelineInput(
                codigo=codigo,
                interpretador_cls=interpretador_cls,
                safe_mode=self._seguro_repl,
                extra_validators=self._extra_validators_repl,
                interpretador=self._interpretador_persistente,
            ),
        )
        self._interpretador_persistente = setup.interpretador
        self._seguro_repl = setup.safe_mode
        self._extra_validators_repl = setup.validadores_extra
        if _resultado_pipeline is not None:
            self._delegate._imprimir_resultado_repl(
                _resultado_pipeline.ast,
                _resultado_pipeline.resultado,
            )

    def run(self, args: Any) -> int:
        buffer: list[str] = []
        self._delegate._estado_repl = self._delegate._crear_estado_repl()
        self._seguro_repl = bool(getattr(args, "seguro", True))
        self._extra_validators_repl = getattr(args, "extra_validators", None)
        interpretador_cls = resolver_interpretador_cls(
            module_name=__name__,
            default_cls=InterpretadorCobra,
        )

        sandbox = bool(getattr(args, "sandbox", False))
        sandbox_docker = getattr(args, "sandbox_docker", None)

        while True:
            try:
                linea = input(">>> " if not buffer else "... ")
            except KeyboardInterrupt:
                if buffer:
                    mostrar_info(_("Entrada multilinea cancelada."))
                    buffer.clear()
                    self._delegate._estado_repl = self._delegate._crear_estado_repl()
                    continue
                mostrar_info(_("Interrupción recibida. Saliendo del REPL."))
                break
            except EOFError:
                if buffer:
                    mostrar_info(_("Entrada multilinea cancelada por fin de archivo."))
                    buffer.clear()
                    self._delegate._estado_repl = self._delegate._crear_estado_repl()
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
                    buffer.clear()
                    self._delegate._estado_repl = self._delegate._crear_estado_repl()
                else:
                    mostrar_info(_("Saliendo..."))
                break

            buffer.append(linea)
            codigo = "\n".join(buffer)
            try:
                prevalidar_y_parsear_codigo(codigo)
            except (LexerError, ParserError) as err:
                if self.es_error_de_bloque_incompleto(err):
                    continue
                categoria = self._delegate._clasificar_error_repl(err)
                self._delegate._log_error(categoria, err)
                buffer.clear()
                self._delegate._estado_repl = self._delegate._crear_estado_repl()
                continue
            except Exception as err:
                categoria = self._delegate._clasificar_error_repl(err)
                self._delegate._log_error(categoria, err)
                buffer.clear()
                self._delegate._estado_repl = self._delegate._crear_estado_repl()
                continue

            try:
                if sandbox:
                    self._delegate._ejecutar_en_sandbox(codigo)
                elif sandbox_docker:
                    self._delegate._ejecutar_en_docker(codigo, sandbox_docker)
                else:
                    self._ejecutar_en_modo_normal(codigo, interpretador_cls)
                buffer.clear()
            except (PrimitivaPeligrosaError, RuntimeError) as err:
                categoria = self._delegate._clasificar_error_repl(err)
                self._delegate._log_error(categoria, err)
                buffer.clear()
                self._delegate._estado_repl = self._delegate._crear_estado_repl()
                continue
            except Exception as err:
                categoria = self._delegate._clasificar_error_repl(err)
                self._delegate._log_error(categoria, err)
                buffer.clear()
                self._delegate._estado_repl = self._delegate._crear_estado_repl()
                continue

        return 0
