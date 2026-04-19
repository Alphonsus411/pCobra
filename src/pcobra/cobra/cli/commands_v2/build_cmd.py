from argparse import Namespace
from typing import Any

from pcobra.cobra.cli.commands.base import BaseCommand
from pcobra.cobra.cli.commands.compile_cmd import CompileCommand, LANG_CHOICES
from pcobra.cobra.cli.i18n import _
from pcobra.cobra.cli.utils.autocomplete import files_completer


class BuildCommandV2(BaseCommand):
    """Comando v2 para compilación/transpilación interna."""

    name = "build"
    capability = "codegen"
    requires_sqlite_key: bool = True

    def __init__(self) -> None:
        super().__init__()
        self._legacy = CompileCommand()

    def register_subparser(self, subparsers: Any):
        parser = subparsers.add_parser(self.name, help=_("Build/transpile a Cobra file"))
        parser.add_argument("file", help=_("Source Cobra file")).completer = files_completer()
        parser.add_argument("--target", choices=LANG_CHOICES, help=_("Target language"))
        parser.add_argument(
            "--targets",
            help=_("Comma-separated target languages"),
        )
        parser.set_defaults(cmd=self)
        return parser

    def run(self, args: Any) -> int:
        target = getattr(args, "target", None) or "python"
        legacy_args = Namespace(
            archivo=args.file,
            tipo=target,
            backend=target,
            tipos=getattr(args, "targets", None),
            modo=getattr(args, "modo", "mixto"),
        )
        return self._legacy.run(legacy_args)
