from __future__ import annotations

import ast
import compileall
import json
import py_compile
import shutil
import subprocess
import tempfile
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Callable

from pcobra.cobra.cli.commands.base import BaseCommand
from pcobra.cobra.cli.i18n import _
from pcobra.cobra.cli.mode_policy import validar_politica_modo
from pcobra.cobra.cli.utils.argument_parser import CustomArgumentParser
from pcobra.cobra.cli.utils.messages import mostrar_error, mostrar_info


@dataclass
class ValidationResult:
    status: str
    message: str


@dataclass
class TargetSummary:
    ok: int = 0
    fail: int = 0
    skipped: int = 0


@dataclass
class SyntaxReport:
    python: ValidationResult
    cobra: ValidationResult
    targets: dict[str, TargetSummary] = field(default_factory=dict)
    strict: bool = False


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


def _tokenize(lexer):
    if hasattr(lexer, "tokenizar"):
        return lexer.tokenizar()
    if hasattr(lexer, "analizar_token"):
        return lexer.analizar_token()
    raise AttributeError("Lexer no expone tokenizar() ni analizar_token().")


def _run_command(command: list[str], cwd: Path | None = None) -> tuple[bool, str]:
    result = subprocess.run(
        command,
        cwd=str(cwd) if cwd else None,
        text=True,
        capture_output=True,
    )
    if result.returncode == 0:
        return True, ""
    return False, (result.stderr or result.stdout).strip()


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
    from pcobra.cobra.core import Lexer, Parser

    for fixture in COBRA_FIXTURES:
        if not fixture.exists():
            return ValidationResult("fail", f"Fixture no encontrado: {fixture}")

    for fixture in COBRA_FIXTURES:
        code = fixture.read_text(encoding="utf-8")
        try:
            tokens = _tokenize(Lexer(code))
            Parser(tokens).parsear()
        except Exception as exc:  # noqa: BLE001
            rel_path = fixture.relative_to(SRC_DIR.parent)
            return ValidationResult("fail", f"Parse falló en {rel_path}: {exc}")

    return ValidationResult("ok", "Parse básico Cobra correcto")


def _validate_python(code: str) -> ValidationResult:
    try:
        ast.parse(code)
    except SyntaxError as exc:
        return ValidationResult("fail", f"ast.parse falló: {exc}")
    return ValidationResult("ok", "ast.parse correcto")


def _validate_javascript(code: str) -> ValidationResult:
    node = shutil.which("node")
    if not node:
        return ValidationResult("skipped", "node no está disponible")
    with tempfile.TemporaryDirectory(prefix="pcobra_js_") as tmp:
        file_path = Path(tmp) / "main.js"
        file_path.write_text(code, encoding="utf-8")
        ok, output = _run_command([node, "--check", str(file_path)])
    return ValidationResult("ok", "node --check correcto") if ok else ValidationResult("fail", output)


def _validate_rust(code: str) -> ValidationResult:
    rustc = shutil.which("rustc")
    if not rustc:
        return ValidationResult("skipped", "rustc no está disponible")
    normalized = "\n".join(
        line
        for line in code.splitlines()
        if line.strip() not in {"use crate::corelibs::*;", "use crate::standard_library::*;"}
    )
    if "fn main(" not in normalized:
        body = "\n".join(f"    {line}" for line in normalized.splitlines() if line.strip())
        normalized = f"fn main() {{\n{body}\n}}"
    with tempfile.TemporaryDirectory(prefix="pcobra_rust_") as tmp:
        file_path = Path(tmp) / "main.rs"
        output_file = Path(tmp) / "main.rmeta"
        file_path.write_text(normalized, encoding="utf-8")
        ok, output = _run_command(
            [rustc, "--emit=metadata", "--edition=2021", str(file_path), "-o", str(output_file)]
        )
    return ValidationResult("ok", "rustc --emit=metadata correcto") if ok else ValidationResult("fail", output)


def _validate_go(code: str) -> ValidationResult:
    gofmt = shutil.which("gofmt")
    if not gofmt:
        return ValidationResult("skipped", "gofmt no está disponible")
    with tempfile.TemporaryDirectory(prefix="pcobra_go_") as tmp:
        file_path = Path(tmp) / "main.go"
        file_path.write_text(code, encoding="utf-8")
        ok, output = _run_command([gofmt, "-l", str(file_path)])
    return ValidationResult("ok", "gofmt -l correcto") if ok else ValidationResult("fail", output)


def _validate_cpp(code: str) -> ValidationResult:
    clangpp = shutil.which("clang++")
    if not clangpp:
        return ValidationResult("skipped", "clang++ no está disponible")
    normalized = "\n".join(
        line
        for line in code.splitlines()
        if not line.strip().startswith("#include <pcobra/")
    )
    with tempfile.TemporaryDirectory(prefix="pcobra_cpp_") as tmp:
        file_path = Path(tmp) / "main.cpp"
        file_path.write_text(normalized, encoding="utf-8")
        ok, output = _run_command([clangpp, "-fsyntax-only", str(file_path)])
    return ValidationResult("ok", "clang++ -fsyntax-only correcto") if ok else ValidationResult("fail", output)


def _validate_java(code: str) -> ValidationResult:
    javac = shutil.which("javac")
    if not javac:
        return ValidationResult("skipped", "javac no está disponible")
    normalized = "\n".join(
        line for line in code.splitlines() if not line.strip().startswith("import pcobra.")
    )
    with tempfile.TemporaryDirectory(prefix="pcobra_java_") as tmp:
        file_path = Path(tmp) / "Main.java"
        file_path.write_text(normalized, encoding="utf-8")
        ok, output = _run_command([javac, str(file_path)], cwd=Path(tmp))
    return ValidationResult("ok", "javac correcto") if ok else ValidationResult("fail", output)


def _validate_wasm(code: str) -> ValidationResult:
    wat2wasm = shutil.which("wat2wasm")
    if not wat2wasm:
        return ValidationResult("skipped", "wat2wasm no está disponible")
    with tempfile.TemporaryDirectory(prefix="pcobra_wasm_") as tmp:
        file_path = Path(tmp) / "main.wat"
        output_file = Path(tmp) / "main.wasm"
        file_path.write_text(code, encoding="utf-8")
        ok, output = _run_command([wat2wasm, str(file_path), "-o", str(output_file)])
    return ValidationResult("ok", "wat2wasm correcto") if ok else ValidationResult("fail", output)


def _validate_asm(code: str) -> ValidationResult:
    lines = [line.strip() for line in code.splitlines() if line.strip()]
    if not lines:
        return ValidationResult("fail", "salida ASM vacía")
    unresolved = [line for line in lines if line.startswith("<") and line.endswith(">")]
    if unresolved:
        return ValidationResult("fail", f"tokens ASM no resueltos: {unresolved[:3]}")
    return ValidationResult("ok", "validador interno ASM correcto")


VALIDATORS: dict[str, Callable[[str], ValidationResult]] = {
    "python": _validate_python,
    "javascript": _validate_javascript,
    "rust": _validate_rust,
    "go": _validate_go,
    "cpp": _validate_cpp,
    "java": _validate_java,
    "wasm": _validate_wasm,
    "asm": _validate_asm,
}


class ValidarSintaxisCommand(BaseCommand):
    name = "validar-sintaxis"
    requires_sqlite_key: bool = False

    def register_subparser(self, subparsers: Any) -> CustomArgumentParser:
        parser = subparsers.add_parser(
            self.name,
            help=_("Valida sintaxis de Cobra/Python y de transpiladores oficiales"),
        )
        parser.add_argument(
            "--solo-cobra",
            action="store_true",
            help=_("Solo ejecuta validaciones Python+Cobra; omite transpiladores"),
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
            return list(VALIDATORS)
        parsed = [item.strip().lower() for item in targets_raw.split(",") if item.strip()]
        if not parsed:
            raise ValueError(_("La lista --targets está vacía"))
        invalid = sorted(set(parsed) - set(VALIDATORS))
        if invalid:
            raise ValueError(_("Targets no soportados en --targets: {}.").format(", ".join(invalid)))
        return parsed

    def _load_ast_for_fixture(self, fixture: Path):
        from pcobra.cobra.core import Lexer, Parser

        code = fixture.read_text(encoding="utf-8")
        tokens = _tokenize(Lexer(code))
        return Parser(tokens).parsear()

    def _run_transpilers_syntax(self, targets: list[str], strict: bool) -> tuple[dict[str, TargetSummary], bool]:
        from pcobra.cobra.transpilers.registry import build_official_transpilers

        transpilers = build_official_transpilers()
        fixtures = [fixture for fixture in TRANSPILER_FIXTURES if fixture.exists()]
        if not fixtures:
            raise FileNotFoundError(_("No hay fixtures disponibles para validar transpiladores."))

        summaries = {target: TargetSummary() for target in targets}
        has_failures = False

        for fixture in fixtures:
            ast_nodes = self._load_ast_for_fixture(fixture)
            for target in targets:
                validator = VALIDATORS[target]
                transpiler_cls = transpilers[target]
                generated = transpiler_cls().generate_code(ast_nodes)
                code = generated if isinstance(generated, str) else "\n".join(generated)
                result = validator(code)
                if result.status == "ok":
                    summaries[target].ok += 1
                elif result.status == "skipped":
                    summaries[target].skipped += 1
                    if strict:
                        has_failures = True
                else:
                    summaries[target].fail += 1
                    has_failures = True

        return summaries, has_failures

    def _emit_report(self, report: SyntaxReport, destination: str | None) -> None:
        if not destination:
            return

        payload = {
            "python": asdict(report.python),
            "cobra": asdict(report.cobra),
            "targets": {key: asdict(value) for key, value in report.targets.items()},
            "strict": report.strict,
        }
        serialized = json.dumps(payload, ensure_ascii=False, indent=2)
        if destination == "-":
            print(serialized)
            return
        output_path = Path(destination)
        output_path.write_text(serialized + "\n", encoding="utf-8")
        mostrar_info(_("Reporte JSON escrito en {path}").format(path=output_path))

    def run(self, args: Any) -> int:
        try:
            validar_politica_modo(self.name, args)
            strict = bool(getattr(args, "strict", False))
            only_cobra = bool(getattr(args, "solo_cobra", False))
            report_dest = getattr(args, "report_json", None)

            py_result = _validate_python_syntax()
            cobra_result = _validate_cobra_parse()

            has_failures = py_result.status != "ok" or cobra_result.status != "ok"
            summaries: dict[str, TargetSummary] = {}

            if not only_cobra:
                targets = self._parse_targets(str(getattr(args, "targets", "")))
                summaries, transpilers_failed = self._run_transpilers_syntax(targets, strict)
                has_failures = has_failures or transpilers_failed

            report = SyntaxReport(python=py_result, cobra=cobra_result, targets=summaries, strict=strict)
            self._emit_report(report, report_dest)

            if has_failures:
                mostrar_error(_("La validación de sintaxis encontró errores."))
                return 1

            mostrar_info(_("Validación de sintaxis completada correctamente."))
            return 0
        except Exception as exc:
            mostrar_error(_("Error en validar-sintaxis: {}").format(exc))
            return 1
