from __future__ import annotations

import json
from argparse import Namespace
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from pcobra.cobra.cli.commands.base import BaseCommand
from pcobra.cobra.cli.commands.validar_sintaxis_cmd import (
    ValidarSintaxisCommand,
    ValidationResult,
    _validate_cobra_parse,
    _validate_python_syntax,
)
from pcobra.cobra.cli.commands.verify_cmd import VerifyCommand
from pcobra.cobra.cli.i18n import _
from pcobra.cobra.cli.mode_policy import validar_politica_modo
from pcobra.cobra.cli.target_policies import VERIFICATION_EXECUTABLE_TARGETS
from pcobra.cobra.cli.utils.argument_parser import CustomArgumentParser
from pcobra.cobra.cli.utils.messages import mostrar_error, mostrar_info


@dataclass
class RuntimeEquivalenceReport:
    status: str
    targets_requested: list[str]
    targets_executable: list[str]
    exit_code: int | None
    message: str


@dataclass
class QaValidationReport:
    syntax: dict[str, Any]
    transpilers: dict[str, Any]
    runtime_equivalence: dict[str, Any]


class QaValidarCommand(BaseCommand):
    name = "qa-validar"
    capability = "codegen"
    requires_sqlite_key: bool = False
    SCOPE_CHOICES = ("syntax", "runtime", "all")

    def register_subparser(self, subparsers: Any) -> CustomArgumentParser:
        parser = subparsers.add_parser(
            self.name,
            help=_("Orquesta validación de sintaxis y equivalencia de runtime"),
        )
        parser.add_argument(
            "archivo",
            nargs="?",
            help=_("Archivo Cobra para verificación de equivalencia runtime (scope runtime/all)"),
        )
        parser.add_argument(
            "--solo-cobra",
            action="store_true",
            help=_("Solo ejecuta validación base Python+Cobra"),
        )
        parser.add_argument(
            "--targets",
            default="",
            help=_("Lista CSV de targets (python,javascript,rust,go,cpp,java,wasm,asm)"),
        )
        parser.add_argument(
            "--strict",
            action="store_true",
            help=_("Considera skipped como fallo (útil en CI estricta)"),
        )
        parser.add_argument(
            "--scope",
            choices=self.SCOPE_CHOICES,
            default="all",
            help=_("Alcance de qa-validar: syntax, runtime o all"),
        )
        parser.add_argument(
            "--report-json",
            nargs="?",
            const="-",
            help=_("Imprime reporte JSON (sin ruta) o lo escribe en la ruta indicada"),
        )
        parser.set_defaults(cmd=self)
        return parser

    def _emit_report(self, report: QaValidationReport, destination: str | None) -> None:
        if not destination:
            return
        serialized = json.dumps(asdict(report), ensure_ascii=False, indent=2)
        if destination == "-":
            print(serialized)
            return
        output_path = Path(destination)
        output_path.write_text(serialized + "\n", encoding="utf-8")
        mostrar_info(_("Reporte JSON escrito en {path}").format(path=output_path))

    def _run_syntax_scope(self, args: Any) -> tuple[dict[str, Any], dict[str, Any], bool]:
        syntax_command = ValidarSintaxisCommand()
        strict = bool(getattr(args, "strict", False))
        only_cobra = bool(getattr(args, "solo_cobra", False))

        py_result = _validate_python_syntax()
        cobra_result = _validate_cobra_parse()
        has_failures = py_result.status != "ok" or cobra_result.status != "ok"

        transpilers: dict[str, Any] = {
            "status": "skipped",
            "targets": {},
            "strict": strict,
            "message": "omitido por --solo-cobra" if only_cobra else "sin ejecución",
        }

        if not only_cobra:
            targets = syntax_command._parse_targets(str(getattr(args, "targets", "")))
            summaries, transpilers_failed = syntax_command._run_transpilers_syntax(targets, strict)
            has_failures = has_failures or transpilers_failed
            transpilers = {
                "status": "fail" if transpilers_failed else "ok",
                "targets": {key: asdict(value) for key, value in summaries.items()},
                "strict": strict,
                "message": "validación de transpiladores completada",
            }

        syntax = {
            "status": "fail" if has_failures else "ok",
            "python": asdict(py_result),
            "cobra": asdict(cobra_result),
            "strict": strict,
        }
        return syntax, transpilers, has_failures

    def _run_runtime_scope(self, args: Any) -> tuple[RuntimeEquivalenceReport, bool]:
        strict = bool(getattr(args, "strict", False))
        if bool(getattr(args, "solo_cobra", False)):
            return (
                RuntimeEquivalenceReport(
                    status="skipped",
                    targets_requested=[],
                    targets_executable=[],
                    exit_code=None,
                    message="omitido por --solo-cobra",
                ),
                False,
            )

        if not getattr(args, "archivo", None):
            raise ValueError(_("El argumento 'archivo' es obligatorio para scope runtime/all"))

        syntax_command = ValidarSintaxisCommand()
        requested_targets = syntax_command._parse_targets(str(getattr(args, "targets", "")))
        executable_targets = [t for t in requested_targets if t in VERIFICATION_EXECUTABLE_TARGETS]

        if not executable_targets:
            message = "no hay targets con runtime ejecutable en --targets"
            status = "fail" if strict else "skipped"
            return (
                RuntimeEquivalenceReport(
                    status=status,
                    targets_requested=requested_targets,
                    targets_executable=[],
                    exit_code=None,
                    message=message,
                ),
                strict,
            )

        verify_args = Namespace(
            modo=getattr(args, "modo", "mixto"),
            archivo=getattr(args, "archivo"),
            lenguajes=executable_targets,
        )
        rc = VerifyCommand().run(verify_args)
        has_failures = rc != 0
        message = "equivalencia runtime verificada" if rc == 0 else "falló equivalencia runtime"

        return (
            RuntimeEquivalenceReport(
                status="ok" if rc == 0 else "fail",
                targets_requested=requested_targets,
                targets_executable=executable_targets,
                exit_code=rc,
                message=message,
            ),
            has_failures,
        )

    def run(self, args: Any) -> int:
        try:
            validar_politica_modo(self.name, args, capability=self.capability)
            scope = str(getattr(args, "scope", "all"))
            has_failures = False

            syntax_section = {
                "status": "skipped",
                "python": asdict(ValidationResult("skipped", "scope runtime")),
                "cobra": asdict(ValidationResult("skipped", "scope runtime")),
                "strict": bool(getattr(args, "strict", False)),
            }
            transpilers_section = {
                "status": "skipped",
                "targets": {},
                "strict": bool(getattr(args, "strict", False)),
                "message": "scope runtime",
            }
            runtime_section = RuntimeEquivalenceReport(
                status="skipped",
                targets_requested=[],
                targets_executable=[],
                exit_code=None,
                message="scope syntax",
            )

            if scope in {"syntax", "all"}:
                syntax_section, transpilers_section, syntax_failed = self._run_syntax_scope(args)
                has_failures = has_failures or syntax_failed

            if scope in {"runtime", "all"}:
                runtime_section, runtime_failed = self._run_runtime_scope(args)
                has_failures = has_failures or runtime_failed

            report = QaValidationReport(
                syntax=syntax_section,
                transpilers=transpilers_section,
                runtime_equivalence=asdict(runtime_section),
            )
            self._emit_report(report, getattr(args, "report_json", None))

            if has_failures:
                mostrar_error(_("qa-validar detectó errores."))
                return 1

            mostrar_info(_("qa-validar completado correctamente."))
            return 0
        except Exception as exc:
            mostrar_error(_("Error en qa-validar: {}" ).format(exc))
            return 1
