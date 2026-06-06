from typing import Any

from pcobra.cobra.cli.commands.base import BaseCommand
from pcobra.cobra.cli.i18n import _
from pcobra.cobra.cli.services.contracts import TestRequest
from pcobra.cobra.cli.services.test_service import TestService, VALID_EXTENSIONS
from pcobra.cobra.build import backend_pipeline
from pcobra.cobra.core.sandbox import ejecutar_en_contenedor, ejecutar_en_sandbox, ejecutar_en_sandbox_js
from pcobra.cobra.cli.target_policies import (
    OFFICIAL_TRANSPILATION_TARGETS,
    OFFICIAL_TRANSPILATION_TARGETS_HELP,
    VERIFICATION_EXECUTABLE_TARGETS,
    VERIFICATION_EXECUTABLE_TARGETS_HELP,
    build_runtime_capability_message,
    parse_restricted_target_list,
)
from pcobra.cobra.cli.utils.argument_parser import CustomArgumentParser
from pcobra.cobra.cli.utils.messages import mostrar_error


def _target_cli_choices(values: tuple[str, ...] | list[str]) -> tuple[str, ...]:
    return tuple(values)


class VerifyCommand(BaseCommand):
    """Adaptador legacy de `verificar` hacia TestService."""

    name = "verificar"
    capability = "codegen"
    requires_sqlite_key: bool = False
    OFFICIAL_LANGUAGE_CHOICES = _target_cli_choices(OFFICIAL_TRANSPILATION_TARGETS)
    SUPPORTED_LANGUAGES = _target_cli_choices(VERIFICATION_EXECUTABLE_TARGETS)

    def __init__(self) -> None:
        super().__init__()
        self._service = TestService()

    def _validate_file(self, file_path: str) -> None:
        """Compatibilidad: delega validación de archivo en TestService."""
        self._service.validate_file(file_path)

    def _compile_and_execute(self, ast: Any, lang: str, transpiler: Any | None = None):
        """Compatibilidad: compila/ejecuta un AST o transpilador explícito."""
        try:
            codigo_gen = transpiler.generate_code(ast) if transpiler is not None else backend_pipeline.transpile(ast, lang)
            if lang == "python":
                salida = ejecutar_en_sandbox(codigo_gen)
            elif lang == "javascript":
                salida = ejecutar_en_sandbox_js(codigo_gen)
            elif lang in {"cpp", "rust"}:
                salida = ejecutar_en_contenedor(codigo_gen, lang)
            else:
                return None, _("Runtime no soportado para {}").format(lang)
            return salida.replace("\r\n", "\n"), None
        except ValueError:
            return None, _("Transpilador no encontrado para {}").format(lang)
        except Exception as exc:
            return None, str(exc)

    def register_subparser(self, subparsers: Any) -> CustomArgumentParser:
        parser = subparsers.add_parser(self.name, help=_("Comprueba la salida en varios lenguajes"))
        parser.add_argument("archivo", help=_("Archivo de código fuente a verificar"))
        parser.add_argument(
            "--lenguajes",
            "-l",
            required=True,
            type=lambda value: parse_restricted_target_list(
                value, self.SUPPORTED_LANGUAGES, "verificación ejecutable"
            ),
            help=_(
                "Lista de lenguajes separados por comas para verificación ejecutable. "
                "Targets oficiales de salida: {official}. "
                "Targets con runtime oficial de verificación: {runtime}. "
                "Aquí se compara ejecución real, no solo generación de código. {policy}"
            ).format(
                official=OFFICIAL_TRANSPILATION_TARGETS_HELP,
                runtime=VERIFICATION_EXECUTABLE_TARGETS_HELP,
                policy=build_runtime_capability_message(
                    capability="verificación ejecutable",
                    allowed_targets=VERIFICATION_EXECUTABLE_TARGETS,
                ),
            ),
        )
        parser.set_defaults(cmd=self)
        return parser

    def run(self, args: Any) -> int:
        request = TestRequest(
            archivo=args.archivo,
            lenguajes=list(getattr(args, "lenguajes", []) or []),
            modo=getattr(args, "modo", "mixto"),
        )
        return self._service.run(request)
