from typing import Any

from pcobra.cobra.build import backend_pipeline
from pcobra.cobra.cli.commands.base import BaseCommand
from pcobra.cobra.cli.services import build_service as build_service_module
from pcobra.cobra.cli.services.build_service import BuildService
from pcobra.cobra.cli.i18n import _
from pcobra.cobra.cli.utils.messages import mostrar_error, mostrar_info
from pcobra.cobra.cli.utils.autocomplete import files_completer
from pcobra.cobra.cli.services.installer_build_service import (
    register_installer_build_arguments,
    run_installer_build,
)


class BuildCommandV2(BaseCommand):
    """Comando v2 para compilación/transpilación interna."""

    name = "build"
    capability = "codegen"

    def __init__(self) -> None:
        super().__init__()
        self._service = BuildService()
        self._runtime_manager = self._service._runtime_manager

    def register_subparser(self, subparsers: Any):
        parser = subparsers.add_parser(
            self.name, help=_("Build/transpile a Cobra file")
        )
        parser.add_argument(
            "file",
            nargs="?",
            help=_("Source Cobra file, or project path when --installer is used"),
        ).completer = files_completer()
        parser.add_argument(
            "--installer",
            action="store_true",
            help=_(
                "Build an installer using the same options as 'cobra installer build'"
            ),
        )
        register_installer_build_arguments(
            parser, include_project_path=False, hide_target_help=True
        )
        parser.set_defaults(cmd=self)
        return parser

    def run(self, args: Any) -> int:
        if bool(getattr(args, "installer", False)):
            args.project_path = args.file or "."
            return run_installer_build(args)

        # Compatibilidad de frontera pública: las pruebas e integraciones v2
        # parchean dependencias desde este módulo, pero la implementación
        # canónica vive en BuildService. Sincronizamos esas referencias antes
        # de delegar para no duplicar lógica de build.
        self._service._runtime_manager = self._runtime_manager
        build_service_module.backend_pipeline = backend_pipeline
        build_service_module.mostrar_error = mostrar_error
        build_service_module.mostrar_info = mostrar_info
        return self._service.run(args)
