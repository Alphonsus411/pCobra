"""Validadores internos legacy para regresión histórica.

Este módulo no forma parte de la API pública de validación de sintaxis.
Los comandos públicos deben consumir ``pcobra.cobra.qa.syntax_validation.VALIDATORS``,
que contiene exclusivamente los backends oficiales: python, javascript y rust.
"""

from __future__ import annotations

import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Callable

from pcobra.cobra.qa.syntax_validation import (
    SYNTAX_TOOL_TIMEOUT_SECONDS,
    ValidationResult,
    run_external_command,
)


def _validate_go(code: str) -> ValidationResult:
    go = shutil.which("go")
    if not go:
        return ValidationResult("skipped", "go no está disponible")
    gofmt = shutil.which("gofmt")
    with tempfile.TemporaryDirectory(prefix="pcobra_go_") as tmp:
        file_path = Path(tmp) / "main.go"
        output_file = Path(tmp) / "main.bin"
        file_path.write_text(code, encoding="utf-8")
        try:
            ok, output = run_external_command(
                [go, "build", "-o", str(output_file), str(file_path)],
                timeout_seconds=SYNTAX_TOOL_TIMEOUT_SECONDS,
            )
        except subprocess.TimeoutExpired:
            return ValidationResult(
                "fail",
                f"go build excedió el timeout de {SYNTAX_TOOL_TIMEOUT_SECONDS}s para target go",
            )
        if not ok:
            return ValidationResult("fail", output)

        if not gofmt:
            return ValidationResult(
                "ok", "go build correcto (sin diagnóstico de gofmt)"
            )

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
            return ValidationResult(
                "ok", "go build correcto; gofmt -l detectó diferencias de formato"
            )

    return ValidationResult("ok", "go build correcto; gofmt -l correcto")


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
        try:
            ok, output = run_external_command(
                [clangpp, "-fsyntax-only", str(file_path)],
                timeout_seconds=SYNTAX_TOOL_TIMEOUT_SECONDS,
            )
        except subprocess.TimeoutExpired:
            return ValidationResult(
                "fail",
                f"clang++ excedió el timeout de {SYNTAX_TOOL_TIMEOUT_SECONDS}s para target cpp",
            )
    return (
        ValidationResult("ok", "clang++ -fsyntax-only correcto")
        if ok
        else ValidationResult("fail", output)
    )


def _validate_java(code: str) -> ValidationResult:
    javac = shutil.which("javac")
    if not javac:
        return ValidationResult("skipped", "javac no está disponible")
    normalized = "\n".join(
        line
        for line in code.splitlines()
        if not line.strip().startswith("import pcobra.")
    )
    with tempfile.TemporaryDirectory(prefix="pcobra_java_") as tmp:
        file_path = Path(tmp) / "Main.java"
        file_path.write_text(normalized, encoding="utf-8")
        try:
            ok, output = run_external_command(
                [javac, str(file_path)],
                cwd=Path(tmp),
                timeout_seconds=SYNTAX_TOOL_TIMEOUT_SECONDS,
            )
        except subprocess.TimeoutExpired:
            return ValidationResult(
                "fail",
                f"javac excedió el timeout de {SYNTAX_TOOL_TIMEOUT_SECONDS}s para target java",
            )
    return (
        ValidationResult("ok", "javac correcto")
        if ok
        else ValidationResult("fail", output)
    )


def _validate_wasm(code: str) -> ValidationResult:
    wat2wasm = shutil.which("wat2wasm")
    if not wat2wasm:
        return ValidationResult("skipped", "wat2wasm no está disponible")
    with tempfile.TemporaryDirectory(prefix="pcobra_wasm_") as tmp:
        file_path = Path(tmp) / "main.wat"
        output_file = Path(tmp) / "main.wasm"
        file_path.write_text(code, encoding="utf-8")
        try:
            ok, output = run_external_command(
                [wat2wasm, str(file_path), "-o", str(output_file)],
                timeout_seconds=SYNTAX_TOOL_TIMEOUT_SECONDS,
            )
        except subprocess.TimeoutExpired:
            return ValidationResult(
                "fail",
                f"wat2wasm excedió el timeout de {SYNTAX_TOOL_TIMEOUT_SECONDS}s para target wasm",
            )
    return (
        ValidationResult("ok", "wat2wasm correcto")
        if ok
        else ValidationResult("fail", output)
    )


def _validate_asm(code: str) -> ValidationResult:
    lines = [line.strip() for line in code.splitlines() if line.strip()]
    if not lines:
        return ValidationResult("fail", "salida ASM vacía")
    unresolved = [line for line in lines if line.startswith("<") and line.endswith(">")]
    if unresolved:
        return ValidationResult("fail", f"tokens ASM no resueltos: {unresolved[:3]}")
    return ValidationResult("ok", "validador interno ASM correcto")


LEGACY_INTERNAL_VALIDATORS: dict[str, Callable[[str], ValidationResult]] = {
    "go": _validate_go,
    "cpp": _validate_cpp,
    "java": _validate_java,
    "wasm": _validate_wasm,
    "asm": _validate_asm,
}

__all__ = ["LEGACY_INTERNAL_VALIDATORS"]
