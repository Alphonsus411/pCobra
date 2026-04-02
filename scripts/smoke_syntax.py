#!/usr/bin/env python3
"""Smoke check rápido: sintaxis Python y parseo básico de fixtures Cobra."""

from __future__ import annotations

import compileall
import py_compile
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = ROOT / "src"
TESTS_DIR = ROOT / "tests"

# Fixtures representativos para validar tokenización + parseo Cobra.
COBRA_FIXTURES = [
    ROOT / "scripts" / "benchmarks" / "programs" / "small.co",
    ROOT / "scripts" / "benchmarks" / "programs" / "factorial.co",
    ROOT / "scripts" / "benchmarks" / "programs" / "medium.co",
]


def _run_python_syntax_smoke() -> bool:
    print("🔎 Validando sintaxis Python en src/ y tests/...")

    src_ok = compileall.compile_dir(str(SRC_DIR), quiet=1, force=False)

    # En tests/ hay fixtures de salida que pueden no ser módulos Python válidos
    # (por ejemplo archivos esperados para snapshots). Solo validamos suites
    # ejecutables de test.
    test_candidates = [*TESTS_DIR.glob("test_*.py")]
    test_candidates.extend(TESTS_DIR.rglob("unit/**/*.py"))
    test_candidates.extend(TESTS_DIR.rglob("integration/**/*.py"))
    tests_ok = True
    for file_path in test_candidates:
        try:
            py_compile.compile(str(file_path), doraise=True)
        except py_compile.PyCompileError as exc:
            print(f"❌ Error de sintaxis en {file_path.relative_to(ROOT)}: {exc.msg}")
            tests_ok = False

    if src_ok and tests_ok:
        print("✅ Sintaxis Python OK.\n")
        return True
    print("❌ Se detectaron errores de sintaxis Python.\n")
    return False


def _tokenize(lexer):
    if hasattr(lexer, "tokenizar"):
        return lexer.tokenizar()
    if hasattr(lexer, "analizar_token"):
        return lexer.analizar_token()
    raise AttributeError("Lexer no expone tokenizar() ni analizar_token().")


def _run_cobra_parse_smoke() -> bool:
    print("🔎 Validando parseo básico Cobra con fixtures .co...")

    sys.path.insert(0, str(SRC_DIR))
    from pcobra.cobra.core import Lexer, Parser

    all_ok = True
    for fixture in COBRA_FIXTURES:
        if not fixture.exists():
            print(f"❌ Fixture no encontrado: {fixture}")
            all_ok = False
            continue

        code = fixture.read_text(encoding="utf-8")
        try:
            tokens = _tokenize(Lexer(code))
            Parser(tokens).parsear()
            print(f"✅ Parse OK: {fixture.relative_to(ROOT)}")
        except Exception as exc:  # noqa: BLE001 - smoke check: reportar todo fallo
            print(f"❌ Parse falló en {fixture.relative_to(ROOT)}: {exc}")
            all_ok = False

    print()
    return all_ok


def main() -> int:
    py_ok = _run_python_syntax_smoke()
    cobra_ok = _run_cobra_parse_smoke()

    if py_ok and cobra_ok:
        print("🎉 Smoke de sintaxis completado correctamente.")
        return 0

    print("🚨 Smoke de sintaxis con errores.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
