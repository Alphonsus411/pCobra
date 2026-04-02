from __future__ import annotations

import ast
import json
import shutil
import subprocess
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable


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
    python: ValidationResult | None = None
    cobra: ValidationResult | None = None
    targets: dict[str, TargetSummary] = field(default_factory=dict)
    strict: bool = False
    errors_by_target: dict[str, list[str]] = field(default_factory=dict)


SUPPORTED_VALIDATOR_TARGETS: tuple[str, ...] = (
    "python",
    "javascript",
    "rust",
    "go",
    "cpp",
    "java",
    "wasm",
    "asm",
)


def _tokenize(lexer):
    if hasattr(lexer, "tokenizar"):
        return lexer.tokenizar()
    if hasattr(lexer, "analizar_token"):
        return lexer.analizar_token()
    raise AttributeError("Lexer no expone tokenizar() ni analizar_token().")


def load_ast_for_fixture(fixture: Path):
    from pcobra.cobra.core import Lexer, Parser

    code = fixture.read_text(encoding="utf-8")
    tokens = _tokenize(Lexer(code))
    return Parser(tokens).parsear()


def run_external_command(command: list[str], cwd: Path | None = None) -> tuple[bool, str]:
    result = subprocess.run(
        command,
        cwd=str(cwd) if cwd else None,
        text=True,
        capture_output=True,
    )
    if result.returncode == 0:
        return True, ""
    return False, (result.stderr or result.stdout).strip()


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
        ok, output = run_external_command([node, "--check", str(file_path)])
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
        ok, output = run_external_command(
            [rustc, "--emit=metadata", "--edition=2021", str(file_path), "-o", str(output_file)]
        )
    return ValidationResult("ok", "rustc --emit=metadata correcto") if ok else ValidationResult("fail", output)


def _validate_go(code: str) -> ValidationResult:
    go = shutil.which("go")
    if not go:
        return ValidationResult("skipped", "go no está disponible")
    gofmt = shutil.which("gofmt")
    with tempfile.TemporaryDirectory(prefix="pcobra_go_") as tmp:
        file_path = Path(tmp) / "main.go"
        output_file = Path(tmp) / "main.bin"
        file_path.write_text(code, encoding="utf-8")
        ok, output = run_external_command([go, "build", "-o", str(output_file), str(file_path)])
        if not ok:
            return ValidationResult("fail", output)

        if not gofmt:
            return ValidationResult("ok", "go build correcto (sin diagnóstico de gofmt)")

        gofmt_result = subprocess.run(
            [gofmt, "-l", str(file_path)],
            text=True,
            capture_output=True,
        )
        if gofmt_result.returncode != 0:
            message = (gofmt_result.stderr or gofmt_result.stdout).strip()
            return ValidationResult("fail", message or "gofmt -l falló")

        style_output = gofmt_result.stdout.strip()
        if style_output:
            return ValidationResult("ok", "go build correcto; gofmt -l detectó diferencias de formato")

    return ValidationResult("ok", "go build correcto; gofmt -l correcto")


def _validate_cpp(code: str) -> ValidationResult:
    clangpp = shutil.which("clang++")
    if not clangpp:
        return ValidationResult("skipped", "clang++ no está disponible")
    normalized = "\n".join(
        line for line in code.splitlines() if not line.strip().startswith("#include <pcobra/")
    )
    with tempfile.TemporaryDirectory(prefix="pcobra_cpp_") as tmp:
        file_path = Path(tmp) / "main.cpp"
        file_path.write_text(normalized, encoding="utf-8")
        ok, output = run_external_command([clangpp, "-fsyntax-only", str(file_path)])
    return ValidationResult("ok", "clang++ -fsyntax-only correcto") if ok else ValidationResult("fail", output)


def _validate_java(code: str) -> ValidationResult:
    javac = shutil.which("javac")
    if not javac:
        return ValidationResult("skipped", "javac no está disponible")
    normalized = "\n".join(line for line in code.splitlines() if not line.strip().startswith("import pcobra."))
    with tempfile.TemporaryDirectory(prefix="pcobra_java_") as tmp:
        file_path = Path(tmp) / "Main.java"
        file_path.write_text(normalized, encoding="utf-8")
        ok, output = run_external_command([javac, str(file_path)], cwd=Path(tmp))
    return ValidationResult("ok", "javac correcto") if ok else ValidationResult("fail", output)


def _validate_wasm(code: str) -> ValidationResult:
    wat2wasm = shutil.which("wat2wasm")
    if not wat2wasm:
        return ValidationResult("skipped", "wat2wasm no está disponible")
    with tempfile.TemporaryDirectory(prefix="pcobra_wasm_") as tmp:
        file_path = Path(tmp) / "main.wat"
        output_file = Path(tmp) / "main.wasm"
        file_path.write_text(code, encoding="utf-8")
        ok, output = run_external_command([wat2wasm, str(file_path), "-o", str(output_file)])
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


def run_transpiler_syntax_validation(
    *,
    fixtures: list[Path],
    targets: list[str],
    transpilers: dict[str, type],
    strict: bool = False,
) -> tuple[SyntaxReport, list[dict[str, str]], bool]:
    summaries: dict[str, TargetSummary] = {target: TargetSummary() for target in targets}
    errors_by_target: dict[str, list[str]] = {target: [] for target in targets}
    events: list[dict[str, str]] = []
    has_failures = False

    for fixture in fixtures:
        try:
            ast_nodes = load_ast_for_fixture(fixture)
        except Exception as exc:  # noqa: BLE001
            for target in targets:
                summaries[target].fail += 1
                message = f"parse/transpilación previa falló: {type(exc).__name__}: {exc}"
                events.append(
                    {
                        "fixture": str(fixture),
                        "target": target,
                        "status": "fail",
                        "message": message,
                    }
                )
                errors_by_target[target].append(message)
            has_failures = True
            continue

        for target in targets:
            validator = VALIDATORS.get(target)
            if validator is None:
                summaries[target].fail += 1
                msg = "sin validador configurado"
                events.append(
                    {
                        "fixture": str(fixture),
                        "target": target,
                        "status": "fail",
                        "message": msg,
                    }
                )
                errors_by_target[target].append(msg)
                has_failures = True
                continue

            try:
                transpiler_cls = transpilers[target]
                generated = transpiler_cls().generate_code(ast_nodes)
                code = generated if isinstance(generated, str) else "\n".join(generated)
                result = validator(code)
            except Exception as exc:  # noqa: BLE001
                payload = {
                    "stage": "transpiler_or_validator",
                    "target": target,
                    "fixture": str(fixture),
                    "error": f"{type(exc).__name__}: {exc}",
                }
                message = json.dumps(payload, ensure_ascii=False)
                result = ValidationResult("fail", message)

            events.append(
                {
                    "fixture": str(fixture),
                    "target": target,
                    "status": result.status,
                    "message": result.message,
                }
            )
            if result.status == "ok":
                summaries[target].ok += 1
            elif result.status == "skipped":
                summaries[target].skipped += 1
                if strict:
                    has_failures = True
                    errors_by_target[target].append(result.message)
            else:
                summaries[target].fail += 1
                errors_by_target[target].append(result.message)
                has_failures = True

    report = SyntaxReport(
        targets=summaries,
        strict=strict,
        errors_by_target={target: msgs for target, msgs in errors_by_target.items() if msgs},
    )
    return report, events, has_failures
