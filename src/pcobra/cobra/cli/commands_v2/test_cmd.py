from argparse import Namespace
from typing import Any

from pcobra.cobra.cli.commands.base import BaseCommand
from pcobra.cobra.cli.commands.verify_cmd import VerifyCommand
from pcobra.cobra.cli.i18n import _
from pcobra.cobra.cli.utils.autocomplete import files_completer


class TestCommandV2(BaseCommand):
    """Comando v2 para validación de proyectos Cobra."""

    name = "test"
    capability = "codegen"

    def __init__(self) -> None:
        super().__init__()
        self._legacy = VerifyCommand()

    def register_subparser(self, subparsers: Any):
        parser = subparsers.add_parser(self.name, help=_("Validate project output across runtimes"))
        parser.add_argument("file", help=_("Source Cobra file")).completer = files_completer()
        parser.add_argument(
            "--langs",
            "-l",
            required=True,
            help=_("Comma-separated runtime languages to validate"),
        )
        parser.set_defaults(cmd=self)
        return parser

    def run(self, args: Any) -> int:
        legacy_args = Namespace(
            archivo=args.file,
            lenguajes=getattr(args, "langs", ""),
            modo=getattr(args, "modo", "mixto"),
        )
        return self._legacy.run(legacy_args)
