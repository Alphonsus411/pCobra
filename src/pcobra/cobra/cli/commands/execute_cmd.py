import sys
from typing import Any

from pcobra.cobra.bindings.runtime_manager import RuntimeManager
from pcobra.cobra.cli.commands.base import BaseCommand
from pcobra.cobra.cli.i18n import _
from pcobra.cobra.cli.services.contracts import RunRequest
from pcobra.cobra.cli.services.run_service import (
    LEGACY_SANDBOX_COMPAT_FLAG,
    RunService,
    detectar_raiz_proyecto_desde_archivo as _detectar_raiz_proyecto_desde_archivo,
    ejecutar_en_contenedor,
    ejecutar_en_sandbox,
    sandbox_module,
    validar_dependencias,
)
from pcobra.cobra.cli.target_policies import (
    DOCKER_EXECUTABLE_TARGETS,
    OFFICIAL_RUNTIME_TARGETS_HELP,
    build_runtime_capability_message,
    parse_runtime_target,
    resolve_docker_backend,
)
from pcobra.cobra.cli.utils.autocomplete import files_completer
from pcobra.cobra.cli.utils.messages import mostrar_error

sys.modules.setdefault("cli.commands.execute_cmd", sys.modules[__name__])
RUNTIME_MANAGER = RuntimeManager()


class ExecuteCommand(BaseCommand):
    """Adaptador legacy de `ejecutar` hacia RunService."""

    name = "ejecutar"
    capability = "execute"

    def __init__(self) -> None:
        super().__init__()
        self._service = RunService()

    def register_subparser(self, subparsers):
        parser = subparsers.add_parser(self.name, help=_("Ejecuta un script Cobra"))
        parser.add_argument("archivo", help=_("Ruta al archivo a ejecutar")).completer = files_completer()
        parser.add_argument("--debug", action="store_true", default=False, help=_("Show debug messages"))
        parser.add_argument("--sandbox", action="store_true", help=_("Ejecuta el código en una sandbox"))
        parser.add_argument(
            "--contenedor",
            type=lambda value: parse_runtime_target(
                value,
                allowed_targets=DOCKER_EXECUTABLE_TARGETS,
                capability="ejecución en contenedor Docker",
            ),
            choices=DOCKER_EXECUTABLE_TARGETS,
            help=_(
                "Ejecuta el código en un contenedor Docker con runtime oficial "
                "({targets}). Esta opción ejecuta de verdad el programa; no basta con que el target "
                "sea un target oficial de salida. {policy}"
            ).format(
                targets=OFFICIAL_RUNTIME_TARGETS_HELP,
                policy=build_runtime_capability_message(
                    capability="ejecución en contenedor Docker",
                    allowed_targets=DOCKER_EXECUTABLE_TARGETS,
                ),
            ),
        )
        parser.set_defaults(cmd=self)
        return parser

    def run(self, args: Any) -> int:
        request = RunRequest(
            archivo=args.archivo,
            debug=bool(getattr(args, "debug", False)),
            sandbox=bool(getattr(args, "sandbox", False)),
            contenedor=getattr(args, "contenedor", None),
            formatear=bool(getattr(args, "formatear", False)),
            modo=getattr(args, "modo", "mixto"),
            seguro=bool(getattr(args, "seguro", True)),
            verbose=int(getattr(args, "verbose", 0) or 0),
            depurar=bool(getattr(args, "depurar", False)),
            extra_validators=getattr(args, "extra_validators", None),
            allow_insecure_fallback=bool(getattr(args, "allow_insecure_fallback", False)),
        )
        return self._service.run(request)
