from typing import Any

from pcobra.cobra.cli.commands.base import BaseCommand
from pcobra.cobra.cli.commands.interactive_cmd import InteractiveCommand
from pcobra.cobra.cli.mode_policy import validar_politica_modo
from pcobra.cobra.core.runtime import InterpretadorCobra


class ReplCommandV2(BaseCommand):
    """Comando v2 público para iniciar el REPL de Cobra."""

    name = "repl"
    capability = "execute"

    def __init__(self) -> None:
        super().__init__()
        self._delegate = InteractiveCommand(InterpretadorCobra())
        self._delegate.name = self.name

    def register_subparser(self, subparsers: Any):
        return self._delegate.register_subparser(subparsers)

    def run(self, args: Any) -> int:
        validar_politica_modo(self.name, args, capability=self.capability)
        return self._delegate.run(args)
