#!/usr/bin/env python3
"""Valida cobertura mínima para rollout de features del lenguaje.

Modos:
1) Gate CI por cambios de archivos (--base/--head opcionales):
   si cambia parser o standard_library, exige al menos un test y un doc/matriz.
2) Auditoría rápida por feature-id (--feature-id):
   verifica piezas del checklist en parser/interprete/transpilers/tests/docs/examples.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

PARSER_HINTS: tuple[str, ...] = (
    "src/pcobra/core/parser.py",
    "src/pcobra/cobra/core/parser.py",
    "src/pcobra/cobra/core/lark_parser.py",
    "src/pcobra/core/ast_nodes.py",
    "src/pcobra/cobra/core/ast_nodes.py",
)
INTERPRETER_HINTS: tuple[str, ...] = ("src/pcobra/core/interpreter.py",)
OFFICIAL_TRANSPILER_HINTS: tuple[str, ...] = (
    "src/pcobra/cobra/transpilers/transpiler/to_python.py",
    "src/pcobra/cobra/transpilers/transpiler/to_js.py",
    "src/pcobra/cobra/transpilers/transpiler/to_rust.py",
    "src/pcobra/cobra/transpilers/transpiler/to_go.py",
    "src/pcobra/cobra/transpilers/transpiler/to_cpp.py",
    "src/pcobra/cobra/transpilers/transpiler/to_java.py",
    "src/pcobra/cobra/transpilers/transpiler/to_wasm.py",
    "src/pcobra/cobra/transpilers/transpiler/to_asm.py",
)
MATRIX_HINTS: tuple[str, ...] = (
    "docs/matriz_transpiladores.md",
    "docs/matriz_transpiladores.csv",
    "docs/library_compatibility_matrix.md",
    "docs/language_equivalence_matrix.md",
    "docs/standard_library/matriz_api_runtime.md",
)
DOC_HINTS: tuple[str, ...] = (
    "CONTRIBUTING.md",
    "docs/templates/feature_rollout_checklist.md",
)
TEST_PREFIXES: tuple[str, ...] = ("tests/unit/", "tests/integration/")
STDLIB_PREFIX = "src/pcobra/standard_library/"
DOC_PREFIXES: tuple[str, ...] = ("docs/",)
EXAMPLES_FEATURES_DIR = ROOT / "examples" / "features"


def _run_git(args: list[str]) -> tuple[int, str]:
    proc = subprocess.run(
        ["git", *args],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    return proc.returncode, proc.stdout.strip()


def changed_files(base: str = "", head: str = "") -> set[str]:
    ranges: list[list[str]] = []
    if base and head:
        ranges.append(["diff", "--name-only", f"{base}..{head}"])
    elif base:
        ranges.append(["diff", "--name-only", f"{base}..HEAD"])

    code, merge_base = _run_git(["merge-base", "HEAD", "origin/main"])
    if code == 0 and merge_base:
        ranges.append(["diff", "--name-only", f"{merge_base}..HEAD"])

    ranges.append(["diff", "--name-only", "HEAD~1..HEAD"])

    for args in ranges:
        code, out = _run_git(args)
        if code == 0:
            return {line.strip() for line in out.splitlines() if line.strip()}
    return set()


def _is_parser_or_stdlib_change(path: str) -> bool:
    if path.startswith(STDLIB_PREFIX):
        return True
    return path in PARSER_HINTS


def _has_test_update(files: set[str]) -> bool:
    return any(path.startswith(TEST_PREFIXES) for path in files)


def _has_docs_or_matrix_update(files: set[str]) -> bool:
    if any(path.startswith(DOC_PREFIXES) for path in files):
        return True
    if any(path in DOC_HINTS for path in files):
        return True
    return False


def validate_rollout_gate(files: set[str]) -> list[str]:
    if not any(_is_parser_or_stdlib_change(path) for path in files):
        return []

    errors: list[str] = []
    if not _has_test_update(files):
        errors.append(
            "Cambios en parser/standard_library sin actualización de pruebas "
            "(se espera al menos un archivo en tests/unit o tests/integration)."
        )
    if not _has_docs_or_matrix_update(files):
        errors.append(
            "Cambios en parser/standard_library sin actualización documental/matriz "
            "(se espera al menos un cambio en docs/* o CONTRIBUTING.md)."
        )
    return errors


def _files_containing_token(search_roots: tuple[Path, ...], token: str) -> list[str]:
    hits: list[str] = []
    lowered = token.lower()
    for root in search_roots:
        if not root.exists():
            continue
        for path in root.rglob("*"):
            if not path.is_file():
                continue
            if path.suffix not in {".py", ".md", ".rst", ".txt", ".co", ".csv", ".json", ".yaml", ".yml"}:
                continue
            content = path.read_text(encoding="utf-8", errors="ignore").lower()
            if lowered in content or lowered in path.as_posix().lower():
                hits.append(path.relative_to(ROOT).as_posix())
    return sorted(set(hits))


def audit_feature_id(feature_id: str) -> dict[str, list[str]]:
    feature = feature_id.strip().lower()
    if not feature:
        raise ValueError("feature_id vacío")

    parser_hits = [p for p in PARSER_HINTS if (ROOT / p).exists() and feature in (ROOT / p).read_text(encoding="utf-8", errors="ignore").lower()]
    interpreter_hits = [p for p in INTERPRETER_HINTS if (ROOT / p).exists() and feature in (ROOT / p).read_text(encoding="utf-8", errors="ignore").lower()]
    transpiler_hits = [p for p in OFFICIAL_TRANSPILER_HINTS if (ROOT / p).exists() and feature in (ROOT / p).read_text(encoding="utf-8", errors="ignore").lower()]

    matrix_hits = [p for p in MATRIX_HINTS if (ROOT / p).exists() and feature in (ROOT / p).read_text(encoding="utf-8", errors="ignore").lower()]
    test_hits = _files_containing_token((ROOT / "tests",), feature)
    docs_hits = _files_containing_token((ROOT / "docs", ROOT / "CONTRIBUTING.md"), feature)
    example_path = EXAMPLES_FEATURES_DIR / feature / "minimal.co"
    example_hits = [example_path.relative_to(ROOT).as_posix()] if example_path.exists() else []

    return {
        "parser_ast": parser_hits,
        "interpreter": interpreter_hits,
        "official_transpilers": transpiler_hits,
        "compat_matrices": matrix_hits,
        "tests": test_hits,
        "docs": docs_hits,
        "examples": example_hits,
    }


def _print_feature_report(feature_id: str, evidence: dict[str, list[str]]) -> int:
    missing = [section for section, paths in evidence.items() if not paths]
    if missing:
        print(f"❌ Feature rollout incompleto para '{feature_id}'")
        for section in missing:
            print(f" - falta: {section}")
        return 1

    print(f"✅ Feature rollout completo para '{feature_id}'")
    for section, paths in evidence.items():
        print(f" - {section}: {paths[0]}")
    return 0


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", default="", help="SHA base para diff")
    parser.add_argument("--head", default="", help="SHA head para diff")
    parser.add_argument(
        "--feature-id",
        default="",
        help="Identificador de feature (slug) para auditar checklist mínimo",
    )
    return parser


def main() -> int:
    args = build_arg_parser().parse_args()

    if args.feature_id:
        evidence = audit_feature_id(args.feature_id)
        return _print_feature_report(args.feature_id, evidence)

    files = changed_files(base=args.base.strip(), head=args.head.strip())
    errors = validate_rollout_gate(files)
    if errors:
        print("❌ Gate de rollout de features: FALLÓ", file=sys.stderr)
        for error in errors:
            print(f" - {error}", file=sys.stderr)
        return 1

    print("✅ Gate de rollout de features: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
