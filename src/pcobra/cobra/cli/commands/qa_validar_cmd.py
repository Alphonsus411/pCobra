from __future__ import annotations

import json
from argparse import Namespace
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from pcobra.cobra.cli.commands.base import BaseCommand
from pcobra.cobra.cli.transpiler_registry import (
    cli_transpiler_targets_csv,
    cli_transpilers,
)
from pcobra.cobra.qa.syntax_validation import execute_syntax_validation
from pcobra.cobra.qa.syntax_validation import ValidationResult
from pcobra.cobra.cli.i18n import _
from pcobra.cobra.cli.mode_policy import validar_politica_modo
from pcobra.cobra.cli.services.verification_service import (
    execute_runtime_verification,
    parse_verification_targets,
    resolve_executable_targets,
)
from pcobra.cobra.cli.utils.argument_parser import CustomArgumentParser
from pcobra.cobra.cli.utils.messages import mostrar_error, mostrar_info
from pcobra.cobra.transpilers.compatibility_matrix import build_feature_gap_report


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
            help=_("Lista CSV de targets ({targets})").format(
                targets=cli_transpiler_targets_csv(),
            ),
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
        parser.add_argument(
            "--feature-gap-report",
            nargs="?",
            const="-",
            help=_("Exporta reporte de gaps AST en JSON/Markdown (stdout si se omite ruta)"),
        )
        parser.add_argument(
            "--feature-gap-format",
            choices=("json", "markdown"),
            default="json",
            help=_("Formato de exportación para --feature-gap-report"),
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

    def _build_feature_gap_markdown(self, report: dict[str, list[dict[str, Any]]]) -> str:
        lines = ["# Reporte de gaps de features AST", ""]
        for backend, rows in report.items():
            lines.append(f"## {backend}")
            if not rows:
                lines.append("- Sin gaps detectados.")
                lines.append("")
                continue
            lines.append("| feature | esperado | actual | nodos/visit_* faltantes |")
            lines.append("| --- | --- | --- | --- |")
            for row in rows:
                missing_nodes = row.get("missing_nodes", [])
                missing_text = ", ".join(missing_nodes) if missing_nodes else "-"
                lines.append(
                    f"| {row.get('feature', '-')} | {row.get('expected_level', '-')} | "
                    f"{row.get('actual_level', '-')} | {missing_text} |"
                )
            lines.append("")
        return "\n".join(lines).rstrip() + "\n"

    def _emit_feature_gap_report(self, destination: str | None, report_format: str) -> None:
        if not destination:
            return

        report = build_feature_gap_report()
        if report_format == "markdown":
            serialized = self._build_feature_gap_markdown(report)
        else:
            serialized = json.dumps(report, ensure_ascii=False, indent=2) + "\n"

        if destination == "-":
            print(serialized.rstrip())
            return

        output_path = Path(destination)
        output_path.write_text(serialized, encoding="utf-8")
        mostrar_info(_("Reporte de gaps escrito en {path}").format(path=output_path))

    def _run_syntax_scope(self, args: Any) -> tuple[dict[str, Any], dict[str, Any], bool]:
        strict = bool(getattr(args, "strict", False))
        profile = "solo-cobra" if bool(getattr(args, "solo_cobra", False)) else "completo"

        execution = execute_syntax_validation(
            profile=profile,
            targets_raw=str(getattr(args, "targets", "")),
            strict=strict,
            transpilers=cli_transpilers(),
        )

        transpilers: dict[str, Any] = {
            "status": "fail" if execution.has_failures and profile != "solo-cobra" and execution.report.targets else "ok",
            "targets": {key: asdict(value) for key, value in execution.report.targets.items()},
            "strict": strict,
            "message": "omitido por --solo-cobra" if profile == "solo-cobra" else "validación de transpiladores completada",
        }
        if profile == "solo-cobra":
            transpilers["status"] = "skipped"

        syntax = {
            "status": "fail" if execution.has_failures else "ok",
            "python": asdict(execution.report.python),
            "cobra": asdict(execution.report.cobra),
            "strict": strict,
        }
        return syntax, transpilers, execution.has_failures

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

        requested_targets = parse_verification_targets(str(getattr(args, "targets", "")))
        executable_targets = resolve_executable_targets(requested_targets)

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
        rc = execute_runtime_verification(
            archivo=verify_args.archivo,
            lenguajes=list(verify_args.lenguajes),
        )
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
            self._emit_feature_gap_report(
                getattr(args, "feature_gap_report", None),
                str(getattr(args, "feature_gap_format", "json")).strip().lower() or "json",
            )

            if has_failures:
                mostrar_error(_("qa-validar detectó errores."))
                return 1

            mostrar_info(_("qa-validar completado correctamente."))
            return 0
        except ValueError as exc:
            mostrar_error(str(exc))
            return 1
        except Exception as exc:
            mostrar_error(_("Error en qa-validar: {}" ).format(exc))
            return 1
