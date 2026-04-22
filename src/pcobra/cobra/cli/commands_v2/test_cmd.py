from argparse import Namespace, SUPPRESS
from typing import Any

from pcobra.cobra.build import backend_pipeline
from pcobra.cobra.cli.commands.base import BaseCommand
from pcobra.cobra.architecture.contracts import assert_backend_allowed_for_scope
from pcobra.cobra.bindings.runtime_manager import RuntimeManager
from pcobra.cobra.cli.services.test_service import TestService
from pcobra.cobra.cli.i18n import _
from pcobra.cobra.cli.utils.messages import mostrar_error
from pcobra.cobra.cli.target_policies import (
    VERIFICATION_EXECUTABLE_TARGETS,
    parse_restricted_target_list,
)
from pcobra.cobra.cli.utils.autocomplete import files_completer


class TestCommandV2(BaseCommand):
    """Comando v2 para validación de proyectos Cobra."""

    name = "test"
    capability = "codegen"

    def __init__(self) -> None:
        super().__init__()
        self._service = TestService()
        self._runtime_manager = RuntimeManager()
        self._default_langs = ",".join(VERIFICATION_EXECUTABLE_TARGETS)

    def register_subparser(self, subparsers: Any):
        parser = subparsers.add_parser(self.name, help=_("Validate project output across runtimes"))
        parser.add_argument("file", help=_("Source Cobra file")).completer = files_completer()
        # Compatibilidad interna: selección explícita de runtimes queda fuera de la UX pública.
        parser.add_argument(
            "--langs",
            "-l",
            default=self._default_langs,
            type=lambda value: parse_restricted_target_list(
                value, VERIFICATION_EXECUTABLE_TARGETS, "verificación ejecutable"
            ),
            help=SUPPRESS,
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
            assert_backend_allowed_for_scope(backend=lang, scope="public")
            try:
                sandbox = lang == "python"
                containerized = lang in {"javascript", "rust"}
                self._runtime_manager.validate_command_runtime(
                    lang,
                    command="test",
                    sandbox=sandbox,
                    containerized=containerized,
                )
            except ValueError as exc:
                mostrar_error(str(exc), registrar_log=False)
                return 1

        resolution, _runtime = backend_pipeline.resolve_backend_runtime(args.file, {})
        legacy_args = Namespace(
            archivo=args.file,
            lenguajes=langs,
            modo=getattr(args, "modo", "mixto"),
            backend_reason=resolution.reason_for(debug=debug),
        )
        return self._service.run(legacy_args)
