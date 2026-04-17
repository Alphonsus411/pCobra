from argparse import Namespace
from typing import Any

from pcobra.cobra.build import backend_pipeline
from pcobra.cobra.cli.commands.base import BaseCommand
from pcobra.cobra.cli.commands.execute_cmd import ExecuteCommand
from pcobra.cobra.bindings.runtime_manager import RuntimeManager
from pcobra.cobra.cli.i18n import _
from pcobra.cobra.cli.utils.messages import mostrar_error
from pcobra.cobra.cli.utils.autocomplete import files_completer


class RunCommandV2(BaseCommand):
    """Comando v2 para ejecutar código Cobra."""

    name = "run"
    capability = "execute"

    def __init__(self) -> None:
        super().__init__()
        self._legacy = ExecuteCommand()
        self._runtime_manager = RuntimeManager()

    def register_subparser(self, subparsers: Any):
        parser = subparsers.add_parser(self.name, help=_("Run a Cobra file"))
        parser.add_argument("file", help=_("Path to Cobra file")).completer = files_completer()
        parser.add_argument("--debug", action="store_true", default=False, help=_("Show debug messages"))
        parser.add_argument("--sandbox", action="store_true", help=_("Execute code in sandbox"))
        parser.add_argument(
            "--container",
            dest="container",
            choices=("python", "javascript", "rust"),
            help=_("Run the code in a Docker container runtime"),
        )
        parser.set_defaults(cmd=self)
        return parser

    def run(self, args: Any) -> int:
        debug = bool(getattr(args, "debug", False))
        sandbox = bool(getattr(args, "sandbox", False))
        container = getattr(args, "container", None)
        binding_language = container or "python"
        try:
            self._runtime_manager.validate_command_runtime(
                binding_language,
                command="run",
                sandbox=sandbox,
                containerized=bool(container),
            )
        except ValueError as exc:
            mostrar_error(str(exc), registrar_log=False)
            return 1

        resolution = backend_pipeline.resolve_backend(args.file, {})
        legacy_args = Namespace(
            archivo=args.file,
            debug=bool(getattr(args, "debug", False)),
            sandbox=sandbox,
            contenedor=container,
            formatear=bool(getattr(args, "formatear", False)),
            modo=getattr(args, "modo", "mixto"),
            backend_reason=resolution.reason_for(debug=debug),
        )
        return self._legacy.run(legacy_args)
