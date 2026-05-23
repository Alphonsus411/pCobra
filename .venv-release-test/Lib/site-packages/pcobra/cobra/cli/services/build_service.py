from typing import Any

from pcobra.cobra.architecture.contracts import assert_backend_allowed_for_scope
from pcobra.cobra.bindings.runtime_manager import RuntimeManager
from pcobra.cobra.build import backend_pipeline
from pcobra.cobra.cli.i18n import _
from pcobra.cobra.cli.utils.messages import mostrar_error, mostrar_info


class BuildService:
    def __init__(self) -> None:
        self._runtime_manager = RuntimeManager()

    def run(self, args: Any) -> int:
        debug = bool(getattr(args, "debug", False))
        try:
            build_result = backend_pipeline.build(
                args.file,
                {
                    "debug": debug,
                    "source_file": args.file,
                },
            )
        except Exception as exc:
            mostrar_error(str(exc), registrar_log=False)
            return 1

        if debug and build_result.get("reason"):
            mostrar_info(
                _("Resolución de backend (debug): {reason}").format(reason=build_result["reason"]),
                registrar_log=False,
            )
        runtime_language = str(build_result.get("runtime", {}).get("language", "python"))
        assert_backend_allowed_for_scope(backend=runtime_language, scope="public")
        try:
            self._runtime_manager.validate_command_runtime(runtime_language, command="build")
        except ValueError as exc:
            mostrar_error(str(exc), registrar_log=False)
            return 1
        artifact_path = str(build_result.get("artifact_path") or "<stdout>")
        mostrar_info(_("Artefacto Cobra generado."), registrar_log=False)
        mostrar_info(_("Ruta de artefacto: {path}").format(path=artifact_path), registrar_log=False)
        print(build_result["code"])
        return 0
