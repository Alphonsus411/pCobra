from __future__ import annotations

import compileall
import json
import py_compile
from dataclasses import asdict
from pathlib import Path
from typing import Any

from pcobra.cobra.cli.commands.base import BaseCommand
from pcobra.cobra.cli.i18n import _
from pcobra.cobra.cli.mode_policy import validar_politica_modo
from pcobra.cobra.cli.utils.argument_parser import CustomArgumentParser
from pcobra.cobra.cli.utils.messages import mostrar_error, mostrar_info
from pcobra.cobra.qa.syntax_validation import (
    SUPPORTED_VALIDATOR_TARGETS,
    SyntaxReport,
    ValidationResult,
    load_ast_for_fixture,
    run_transpiler_syntax_validation,
)


def _resolve_project_root() -> Path | None:
    current = Path(__file__).resolve()
    for candidate in current.parents:
        if (candidate / "pyproject.toml").exists() and (candidate / "src").is_dir():
            return candidate
    return None


PROJECT_ROOT = _resolve_project_root()
SRC_DIR = (PROJECT_ROOT / "src") if PROJECT_ROOT else Path(__file__).resolve().parents[5] / "src"
TESTS_DIR = (PROJECT_ROOT / "tests") if PROJECT_ROOT else Path(__file__).resolve().parents[5] / "tests"
COBRA_FIXTURES = [
    SRC_DIR.parent / "scripts" / "benchmarks" / "programs" / "small.co",
    SRC_DIR.parent / "scripts" / "benchmarks" / "programs" / "factorial.co",
    SRC_DIR.parent / "scripts" / "benchmarks" / "programs" / "medium.co",
]
TRANSPILER_FIXTURES = [
    SRC_DIR.parent / "scripts" / "benchmarks" / "programs" / "smoke_assign.co",
    SRC_DIR.parent / "examples" / "smoke_assign.co",
]
SUPPORTED_VALIDATION_PROFILES: tuple[str, ...] = ("solo-cobra", "transpiladores", "completo")


def _validate_python_syntax() -> ValidationResult:
    src_ok = compileall.compile_dir(str(SRC_DIR), quiet=1, force=False)
    test_candidates = [*TESTS_DIR.glob("test_*.py")]
    test_candidates.extend(TESTS_DIR.rglob("unit/**/*.py"))
    test_candidates.extend(TESTS_DIR.rglob("integration/**/*.py"))

    tests_ok = True
    errors: list[str] = []
    for file_path in test_candidates:
        try:
            py_compile.compile(str(file_path), doraise=True)
        except py_compile.PyCompileError as exc:
            rel_path = str(file_path.relative_to(SRC_DIR.parent))
            errors.append(f"{rel_path}: {exc.msg}")
            tests_ok = False

    if src_ok and tests_ok:
        return ValidationResult("ok", "Sintaxis Python correcta en src/ y tests/")
    resumen = " ; ".join(errors[:3]) if errors else "compileall detectó errores"
    return ValidationResult("fail", resumen)


def _validate_cobra_parse() -> ValidationResult:
    for fixture in COBRA_FIXTURES:
        if not fixture.exists():
            return ValidationResult("fail", f"Fixture no encontrado: {fixture}")

    for fixture in COBRA_FIXTURES:
        try:
            load_ast_for_fixture(fixture)
        except Exception as exc:  # noqa: BLE001
            rel_path = fixture.relative_to(SRC_DIR.parent)
            return ValidationResult("fail", f"Parse falló en {rel_path}: {exc}")

    return ValidationResult("ok", "Parse básico Cobra correcto")


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
            help=_("Lista CSV de targets a validar (python,javascript,rust,go,cpp,java,wasm,asm)"),
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

    def _run_transpilers_syntax(self, targets: list[str], strict: bool) -> tuple[dict[str, Any], dict[str, list[str]], bool]:
        from pcobra.cobra.transpilers.registry import build_official_transpilers

        transpilers = build_official_transpilers()
        fixtures = [fixture for fixture in TRANSPILER_FIXTURES if fixture.exists()]
        if not fixtures:
            raise FileNotFoundError(_("No hay fixtures disponibles para validar transpiladores."))

        report, _, has_failures = run_transpiler_syntax_validation(
            fixtures=fixtures,
            targets=targets,
            transpilers=transpilers,
            strict=strict,
        )
        return report.targets, report.errors_by_target, has_failures

    def _emit_report(self, report: SyntaxReport, destination: str | None) -> None:
        if not destination:
            return

        payload = {
            "python": asdict(report.python),
            "cobra": asdict(report.cobra),
            "targets": {key: asdict(value) for key, value in report.targets.items()},
            "strict": report.strict,
        }
        if report.errors_by_target:
            payload["errors_by_target"] = report.errors_by_target
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
            report_dest = getattr(args, "report_json", None)

            if profile not in SUPPORTED_VALIDATION_PROFILES:
                raise ValueError(
                    _("Perfil no soportado en --perfil: {}.").format(profile)
                )

            run_python_cobra = profile in {"solo-cobra", "completo"}
            run_transpilers = profile in {"transpiladores", "completo"}

            py_result = (
                _validate_python_syntax()
                if run_python_cobra
                else ValidationResult("skipped", "Perfil transpiladores: validación Python omitida")
            )
            cobra_result = (
                _validate_cobra_parse()
                if run_python_cobra
                else ValidationResult("skipped", "Perfil transpiladores: parse Cobra omitido")
            )

            has_failures = (
                (run_python_cobra and py_result.status != "ok")
                or (run_python_cobra and cobra_result.status != "ok")
            )
            summaries = {}
            errors_by_target: dict[str, list[str]] = {}

            if run_transpilers:
                targets = self._parse_targets(str(getattr(args, "targets", "")))
                summaries, errors_by_target, transpilers_failed = self._run_transpilers_syntax(targets, strict)
                has_failures = has_failures or transpilers_failed

            report = SyntaxReport(
                python=py_result,
                cobra=cobra_result,
                targets=summaries,
                strict=strict,
                errors_by_target=errors_by_target,
            )
            self._emit_report(report, report_dest)

            if has_failures:
                mostrar_error(_("La validación de sintaxis encontró errores."))
                return 1

            mostrar_info(_("Validación de sintaxis completada correctamente."))
            return 0
        except Exception as exc:
            mostrar_error(_("Error en validar-sintaxis: {}").format(exc))
            return 1
