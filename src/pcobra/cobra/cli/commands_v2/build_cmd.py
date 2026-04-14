from argparse import Namespace
from typing import Any

from pcobra.cobra.cli.commands.base import BaseCommand
from pcobra.cobra.build import backend_pipeline
from pcobra.cobra.cli.commands.compile_cmd import CompileCommand
from pcobra.cobra.cli.i18n import _
from pcobra.cobra.cli.utils.autocomplete import files_completer


class BuildCommandV2(BaseCommand):
    """Comando v2 para compilación/transpilación interna."""

    name = "build"
    capability = "codegen"

    def __init__(self) -> None:
        super().__init__()
        self._legacy = CompileCommand()

    def register_subparser(self, subparsers: Any):
        parser = subparsers.add_parser(self.name, help=_("Build/transpile a Cobra file"))
        parser.add_argument("file", help=_("Source Cobra file")).completer = files_completer()
        parser.set_defaults(cmd=self)
        return parser

    def run(self, args: Any) -> int:
        resolution = backend_pipeline.resolve_backend(args.file, {})
        legacy_args = Namespace(
            archivo=args.file,
            tipo=resolution.backend,
            backend=None,
            tipos=None,
            modo=getattr(args, "modo", "mixto"),
            backend_reason=resolution.reason,
        )
        return self._legacy.run(legacy_args)
