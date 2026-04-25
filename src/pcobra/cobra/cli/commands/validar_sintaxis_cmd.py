from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from pcobra.cobra.cli.commands.base import BaseCommand
from pcobra.cobra.cli.transpiler_registry import (
    cli_transpiler_targets_csv,
    cli_transpilers,
)
from pcobra.cobra.cli.i18n import _
from pcobra.cobra.cli.mode_policy import validar_politica_modo
from pcobra.cobra.cli.utils.argument_parser import CustomArgumentParser
from pcobra.cobra.cli.utils.messages import mostrar_error, mostrar_info
from pcobra.cobra.qa.syntax_validation import (
    SUPPORTED_VALIDATION_PROFILES,
    SUPPORTED_VALIDATOR_TARGETS,
    SyntaxReport,
    TargetSummary,
    ValidationResult,
    build_syntax_report_payload,
    execute_syntax_validation,
    SyntaxValidationExecution,
    run_transpiler_syntax_validation,
    validate_cobra_parse,
    validate_python_syntax,
)

# Backward-compatible aliases for existing imports/tests.
_validate_python_syntax = validate_python_syntax
_validate_cobra_parse = validate_cobra_parse


class ValidarSintaxisCommand(BaseCommand):
    name = "validar-sintaxis"
    capability = "codegen"
    requires_sqlite_key: bool = False

    def register_subparser(self, subparsers: Any) -> CustomArgumentParser:
        parser = subparsers.add_parser(
            self.name,
            help=_("Valida sintaxis de Cobra/Python y de transpiladores oficiales"),
        )
        parser.add_argument(
            "--solo-cobra",
            action="store_true",
            help=_("Alias deprecado de --perfil=solo-cobra"),
        )
        parser.add_argument(
            "--perfil",
            default="completo",
            choices=list(SUPPORTED_VALIDATION_PROFILES),
            help=_(
                "Perfil de validación: solo-cobra (Python+parse Cobra), "
                "transpiladores (solo backends), completo (todo)"
            ),
        )
        parser.add_argument(
            "--targets",
            default="",
            help=_("Lista CSV de targets a validar ({targets})").format(
                targets=cli_transpiler_targets_csv(),
            ),
        )
        parser.add_argument(
            "--strict",
            action="store_true",
            help=_("Considera skipped como fallo (útil en CI estricta)"),
        )
        parser.add_argument(
            "--report-json",
            nargs="?",
            const="-",
            help=_("Imprime reporte JSON (sin ruta) o lo escribe en la ruta indicada"),
        )
        parser.set_defaults(cmd=self)
        return parser

    def _parse_targets(self, targets_raw: str) -> list[str]:
        if not targets_raw.strip():
            return list(SUPPORTED_VALIDATOR_TARGETS)
        parsed = [item.strip().lower() for item in targets_raw.split(",") if item.strip()]
        if not parsed:
            raise ValueError(_("La lista --targets está vacía"))
        invalid = sorted(set(parsed) - set(SUPPORTED_VALIDATOR_TARGETS))
        if invalid:
            raise ValueError(_("Targets no soportados en --targets: {}.").format(", ".join(invalid)))
        return parsed

    def _run_transpilers_syntax(self, targets: list[str], strict: bool) -> tuple[dict[str, TargetSummary], dict[str, list[str]], bool]:
        from pcobra.cobra.qa.syntax_validation import TRANSPILER_FIXTURES

        fixtures = [fixture for fixture in TRANSPILER_FIXTURES if fixture.exists()]
        if not fixtures:
            raise FileNotFoundError(_("No hay fixtures disponibles para validar transpiladores."))

        report, _, has_failures = run_transpiler_syntax_validation(
            fixtures=fixtures,
            targets=targets,
            transpilers=cli_transpilers(),
            strict=strict,
        )
        return report.targets, report.errors_by_target, has_failures

    def _emit_report(self, report: SyntaxReport, destination: str | None, profile: str, targets_requested: list[str]) -> None:
        if not destination:
            return

        payload = build_syntax_report_payload(
            SyntaxValidationExecution(
                report=report,
                profile=profile,
                targets_requested=targets_requested,
                has_failures=False,
            )
        )
        serialized = json.dumps(payload, ensure_ascii=False, indent=2)
        if destination == "-":
            print(serialized)
            return
        output_path = Path(destination)
        output_path.write_text(serialized + "\n", encoding="utf-8")
        mostrar_info(_("Reporte JSON escrito en {path}").format(path=output_path))

    def run(self, args: Any) -> int:
        try:
            validar_politica_modo(self.name, args, capability=self.capability)
            strict = bool(getattr(args, "strict", False))
            profile = str(getattr(args, "perfil", "completo")).strip().lower() or "completo"
            if bool(getattr(args, "solo_cobra", False)):
                profile = "solo-cobra"

            execution = execute_syntax_validation(
                profile=profile,
                targets_raw=str(getattr(args, "targets", "")),
                strict=strict,
                transpilers=cli_transpilers(),
            )
            self._emit_report(
                execution.report,
                getattr(args, "report_json", None),
                execution.profile,
                execution.targets_requested,
            )

            if execution.has_failures:
                mostrar_error(_("La validación de sintaxis encontró errores."))
                return 1

            mostrar_info(_("Validación de sintaxis completada correctamente."))
            return 0
        except ValueError as exc:
            mostrar_error(str(exc))
            return 1
        except Exception as exc:
            mostrar_error(_("Error en validar-sintaxis: {}").format(exc))
            return 1
