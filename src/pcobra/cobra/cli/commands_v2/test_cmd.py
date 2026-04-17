from argparse import Namespace
from typing import Any

from pcobra.cobra.build import backend_pipeline
from pcobra.cobra.cli.commands.base import BaseCommand
from pcobra.cobra.cli.commands.verify_cmd import VerifyCommand
from pcobra.cobra.bindings.runtime_manager import RuntimeManager
from pcobra.cobra.cli.i18n import _
from pcobra.cobra.cli.utils.messages import mostrar_error
from pcobra.cobra.cli.target_policies import (
    VERIFICATION_EXECUTABLE_TARGETS,
    VERIFICATION_EXECUTABLE_TARGETS_HELP,
    parse_restricted_target_list,
)
from pcobra.cobra.cli.utils.autocomplete import files_completer


class TestCommandV2(BaseCommand):
    """Comando v2 para validación de proyectos Cobra."""

    name = "test"
    capability = "codegen"

    def __init__(self) -> None:
        super().__init__()
        self._legacy = VerifyCommand()
        self._runtime_manager = RuntimeManager()
        self._default_langs = ",".join(VERIFICATION_EXECUTABLE_TARGETS)

    def register_subparser(self, subparsers: Any):
        parser = subparsers.add_parser(self.name, help=_("Validate project output across runtimes"))
        parser.add_argument("file", help=_("Source Cobra file")).completer = files_completer()
        parser.add_argument(
            "--langs",
            "-l",
            default=self._default_langs,
            type=lambda value: parse_restricted_target_list(
                value, VERIFICATION_EXECUTABLE_TARGETS, "verificación ejecutable"
            ),
            help=_(
                "Comma-separated runtime languages to validate. "
                "Defaults to official verification runtimes: {runtime}."
            ).format(runtime=VERIFICATION_EXECUTABLE_TARGETS_HELP),
        )
        parser.set_defaults(cmd=self)
        return parser

    def run(self, args: Any) -> int:
        debug = bool(getattr(args, "debug", False))
        raw_langs = getattr(args, "langs", self._default_langs)
        if isinstance(raw_langs, str):
            langs = parse_restricted_target_list(
                raw_langs, VERIFICATION_EXECUTABLE_TARGETS, "verificación ejecutable"
            )
        else:
            langs = list(raw_langs)
        for lang in langs:
            try:
                sandbox = lang == "python"
                containerized = lang in {"javascript", "rust"}
                self._runtime_manager.validate_security_route(
                    lang,
                    sandbox=sandbox,
                    containerized=containerized,
                    command="test",
                )
                self._runtime_manager.validate_abi_route(lang)
            except ValueError as exc:
                mostrar_error(str(exc), registrar_log=False)
                return 1

        resolution = backend_pipeline.resolve_backend(args.file, {})
        legacy_args = Namespace(
            archivo=args.file,
            lenguajes=langs,
            modo=getattr(args, "modo", "mixto"),
            backend_reason=resolution.reason_for(debug=debug),
        )
        return self._legacy.run(legacy_args)
