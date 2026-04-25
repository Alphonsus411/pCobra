from typing import Any

from pcobra.cobra.cli.commands.base import BaseCommand
from pcobra.cobra.cli.commands.interactive_cmd import (
    InteractiveCommand,
    SANDBOX_DOCKER_CHOICES,
)
from pcobra.cobra.cli.i18n import _
from pcobra.cobra.core.runtime import InterpretadorCobra
from pcobra.cobra.cli.target_policies import parse_runtime_target


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
        return self._delegate.run(args)
