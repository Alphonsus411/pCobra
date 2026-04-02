#!/usr/bin/env python3
"""Smoke de transpiladores oficiales + validación de sintaxis por backend."""

from __future__ import annotations

import ast
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = ROOT / "src"

COBRA_FIXTURES = [
    ROOT / "scripts" / "benchmarks" / "programs" / "smoke_assign.co",
    ROOT / "examples" / "smoke_assign.co",
]


@dataclass
class ValidationResult:
    status: str
    message: str


@dataclass
class TargetSummary:
    ok: int = 0
    fail: int = 0
    skipped: int = 0


def _tokenize(lexer):
    if hasattr(lexer, "tokenizar"):
        return lexer.tokenizar()
    if hasattr(lexer, "analizar_token"):
        return lexer.analizar_token()
    raise AttributeError("Lexer no expone tokenizar() ni analizar_token().")


def _load_ast_for_fixture(fixture: Path):
    from pcobra.cobra.core import Lexer, Parser

    code = fixture.read_text(encoding="utf-8")
    tokens = _tokenize(Lexer(code))
    return Parser(tokens).parsear()


def _run_command(command: list[str], cwd: Path | None = None) -> tuple[bool, str]:
    result = subprocess.run(
        command,
        cwd=str(cwd) if cwd else None,
        text=True,
        capture_output=True,
    )
    if result.returncode == 0:
        return True, ""
    error_output = (result.stderr or result.stdout).strip()
    return False, error_output


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
    lineas = [line.strip() for line in code.splitlines() if line.strip()]
    if not lineas:
        return ValidationResult("fail", "salida ASM vacía")
    unsupported = [line for line in lineas if line.startswith("<") and line.endswith(">")]
    if unsupported:
        return ValidationResult("fail", f"tokens ASM no resueltos: {unsupported[:3]}")
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


def main() -> int:
    sys.path.insert(0, str(SRC_DIR))

    from pcobra.cobra.transpilers.registry import (
        build_official_transpilers,
        official_transpiler_targets,
    )

    transpilers = build_official_transpilers()
    ordered_targets = official_transpiler_targets()

    fixtures = []
    for fixture in COBRA_FIXTURES:
        if fixture.exists():
            fixtures.append(fixture)
        else:
            print(f"⚠️ Fixture omitido (no existe): {fixture.relative_to(ROOT)}")

    print("🔎 Smoke de sintaxis de transpiladores oficiales")
    print(f"   Targets: {', '.join(ordered_targets)}")
    print(f"   Fixtures: {', '.join(str(f.relative_to(ROOT)) for f in fixtures)}")
    if not fixtures:
        print("❌ No hay fixtures disponibles para ejecutar el smoke.")
        return 1

    summaries: dict[str, TargetSummary] = {target: TargetSummary() for target in ordered_targets}

    required_targets = set(ordered_targets)
    any_required_fail = False
    for fixture in fixtures:
        print(f"\n📦 Fixture: {fixture.relative_to(ROOT)}")
        try:
            ast_nodes = _load_ast_for_fixture(fixture)
        except Exception as exc:  # noqa: BLE001
            print(f"❌ Parse/transpilación previa falló: {exc}")
            for target in ordered_targets:
                summaries[target].fail += 1
            any_required_fail = True
            continue

        for target in ordered_targets:
            transpiler_cls = transpilers[target]
            validator = VALIDATORS.get(target)
            if validator is None:
                print(f"❌ [{target}] sin validador configurado")
                summaries[target].fail += 1
                any_required_fail = True
                continue

            try:
                generated = transpiler_cls().generate_code(ast_nodes)
                code = generated if isinstance(generated, str) else "\n".join(generated)
            except Exception as exc:  # noqa: BLE001
                print(f"❌ [{target}] transpilación falló: {exc}")
                summaries[target].fail += 1
                any_required_fail = True
                continue

            result = validator(code)
            if result.status == "ok":
                print(f"✅ [{target}] {result.message}")
                summaries[target].ok += 1
            elif result.status == "skipped":
                print(f"⏭️  [{target}] {result.message}")
                summaries[target].skipped += 1
            else:
                print(f"❌ [{target}] {result.message}")
                summaries[target].fail += 1
                if target in required_targets:
                    any_required_fail = True

    print("\n📊 Resumen por target")
    for target in ordered_targets:
        summary = summaries[target]
        print(
            f" - {target}: ok={summary.ok} fail={summary.fail} skipped={summary.skipped}"
        )

    if any_required_fail:
        print("\n🚨 Smoke de transpiladores con fallos en targets oficiales.")
        return 1

    print("\n🎉 Smoke de transpiladores completado sin fallos obligatorios.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
