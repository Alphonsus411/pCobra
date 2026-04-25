from typing import Any

from pcobra.cobra.cli.commands.base import BaseCommand
from pcobra.cobra.cli.commands.interactive_cmd import (
    InteractiveCommand,
    SANDBOX_DOCKER_CHOICES,
)
from pcobra.cobra.cli.i18n import _
from pcobra.cobra.cli.utils.messages import mostrar_info
from pcobra.cobra.core.runtime import InterpretadorCobra
from pcobra.cobra.cli.target_policies import parse_runtime_target
from pcobra.cobra.cli.utils.unicode_sanitize import sanitize_input


class ReplCommandV2(BaseCommand):
    """Comando v2 público para iniciar el REPL de Cobra."""

    name = "repl"
    capability = "execute"

    def __init__(self) -> None:
        super().__init__()
        self._delegate = InteractiveCommand(InterpretadorCobra())
        self._delegate.name = self.name

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

    def run(self, args: Any) -> int:
        buffer: list[str] = []
        self._delegate._estado_repl = self._delegate._crear_estado_repl()

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
            if not linea:
                continue

            comando = linea.strip()
            if comando in {"salir", "exit"} and not buffer:
                mostrar_info(_("Saliendo..."))
                break

            try:
                codigo = self._delegate._actualizar_buffer_y_obtener_codigo_listo(
                    buffer,
                    linea,
                )
            except Exception as err:
                categoria = self._delegate._clasificar_error_repl(err)
                self._delegate._log_error(categoria, err)
                buffer.clear()
                self._delegate._estado_repl = self._delegate._crear_estado_repl()
                continue

            if codigo is None:
                continue

            try:
                if sandbox:
                    self._delegate._ejecutar_en_sandbox(codigo)
                elif sandbox_docker:
                    self._delegate._ejecutar_en_docker(codigo, sandbox_docker)
                else:
                    self._delegate.ejecutar_codigo(codigo)
            except Exception as err:
                categoria = self._delegate._clasificar_error_repl(err)
                self._delegate._log_error(categoria, err)
                continue

        return 0
