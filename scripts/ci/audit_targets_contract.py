#!/usr/bin/env python3
"""Gate de auditoría para contrato de targets y matriz de compatibilidad."""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC_ROOT = ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from pcobra.cobra.cli.target_policies import (  # noqa: E402
    OFFICIAL_RUNTIME_TARGETS,
    OFFICIAL_TRANSPILATION_TARGETS,
)
from pcobra.cobra.transpilers.registry import (  # noqa: E402
    TRANSPILER_CLASS_PATHS,
    official_transpiler_targets,
)
from pcobra.cobra.transpilers.targets import OFFICIAL_TARGETS  # noqa: E402

EXPECTED_CANONICAL_TARGETS: tuple[str, ...] = (
    "python",
    "rust",
    "javascript",
    "wasm",
    "go",
    "cpp",
    "java",
    "asm",
)

FORBIDDEN_TERMS: tuple[tuple[re.Pattern[str], str], ...] = (
    (re.compile(r"(?<![\\w/-])hololang(?![\\w/-])", re.IGNORECASE), "hololang"),
    (re.compile(r"(?<![\\w/-])llvm(?![\\w/-])", re.IGNORECASE), "llvm"),
    (re.compile(r"(?<![\\w/-])latex(?![\\w/-])", re.IGNORECASE), "latex"),
    (re.compile(r"(?<![\\w/-])reverse[ -]wasm(?![\\w/-])", re.IGNORECASE), "reverse wasm"),
)

MIN_DOC_PATHS_FOR_MATRIX_CHANGE: tuple[str, ...] = (
    "docs/contrato_runtime_holobit.md",
    "docs/matriz_transpiladores.md",
    "docs/targets_policy.md",
    "docs/compatibility/holobit-sdk.md",
)

CONTRACT_TEST_HINTS: tuple[str, ...] = (
    "tests/unit/test_holobit_backend_contract_matrix.py",
    "tests/unit/test_holobit_sdk_compatibility_report.py",
    "tests/unit/test_official_targets_consistency.py",
    "tests/integration/transpilers/test_official_backends_contracts.py",
    "tests/integration/transpilers/test_backend_contract_canonical_fixtures.py",
)


def _run_git(args: list[str]) -> tuple[int, str]:
    proc = subprocess.run(
        ["git", *args],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    return proc.returncode, proc.stdout.strip()


def _changed_files() -> set[str]:
    base = (sys.argv[1] if len(sys.argv) > 1 else "").strip()
    head = (sys.argv[2] if len(sys.argv) > 2 else "").strip()

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


def validate_canonical_targets() -> list[str]:
    errors: list[str] = []
    if tuple(OFFICIAL_TARGETS) != EXPECTED_CANONICAL_TARGETS:
        errors.append(
            "src/pcobra/cobra/transpilers/targets.py: OFFICIAL_TARGETS desalineado "
            f"(actual={tuple(OFFICIAL_TARGETS)}, esperado={EXPECTED_CANONICAL_TARGETS})"
        )
    return errors


def validate_targets_coherence() -> list[str]:
    errors: list[str] = []
    if tuple(TRANSPILER_CLASS_PATHS) != tuple(OFFICIAL_TARGETS):
        errors.append(
            "src/pcobra/cobra/transpilers/registry.py: claves de TRANSPILER_CLASS_PATHS no "
            "coinciden con OFFICIAL_TARGETS"
        )
    if tuple(official_transpiler_targets()) != tuple(OFFICIAL_TARGETS):
        errors.append(
            "src/pcobra/cobra/transpilers/registry.py: official_transpiler_targets() no "
            "coincide con OFFICIAL_TARGETS"
        )

    transpilation_set = set(OFFICIAL_TRANSPILATION_TARGETS)
    official_set = set(OFFICIAL_TARGETS)
    if transpilation_set != official_set:
        errors.append(
            "src/pcobra/cobra/cli/target_policies.py: OFFICIAL_TRANSPILATION_TARGETS no "
            "coincide exactamente con OFFICIAL_TARGETS"
        )

    runtime_out_of_contract = tuple(
        target for target in OFFICIAL_RUNTIME_TARGETS if target not in official_set
    )
    if runtime_out_of_contract:
        errors.append(
            "src/pcobra/cobra/cli/target_policies.py: OFFICIAL_RUNTIME_TARGETS contiene "
            f"targets fuera del contrato: {runtime_out_of_contract}"
        )
    return errors


def validate_minimal_doc_consistency() -> list[str]:
    errors: list[str] = []
    scan_roots = (
        ROOT / "docs",
        ROOT / "CONTRIBUTING.md",
        ROOT / "README.md",
    )
    files: list[Path] = []
    for item in scan_roots:
        if item.is_dir():
            files.extend(path for path in item.rglob("*") if path.is_file())
        elif item.is_file():
            files.append(item)

    for path in files:
        rel = path.relative_to(ROOT).as_posix()
        content = path.read_text(encoding="utf-8", errors="ignore")
        for pattern, term in FORBIDDEN_TERMS:
            match = pattern.search(content)
            if not match:
                continue
            line_no = content.count("\n", 0, match.start()) + 1
            errors.append(
                f"{rel}:{line_no}: nombre no permitido detectado en documentación/workflow ({term})"
            )
    return errors


def validate_matrix_change_requires_contract_updates(changed_files: set[str]) -> list[str]:
    errors: list[str] = []
    matrix_path = "src/pcobra/cobra/transpilers/compatibility_matrix.py"
    if matrix_path not in changed_files:
        return errors

    doc_updates = [path for path in MIN_DOC_PATHS_FOR_MATRIX_CHANGE if path in changed_files]
    test_updates = [path for path in CONTRACT_TEST_HINTS if path in changed_files]

    if not doc_updates:
        errors.append(
            "Cambió compatibility_matrix.py sin actualizar documentación contractual mínima "
            f"({MIN_DOC_PATHS_FOR_MATRIX_CHANGE})."
        )
    if not test_updates:
        errors.append(
            "Cambió compatibility_matrix.py sin actualizar tests de contrato mínimos "
            f"({CONTRACT_TEST_HINTS})."
        )
    return errors


def main() -> int:
    changed_files = _changed_files()
    checks: tuple[tuple[str, list[str]], ...] = (
        ("set canónico de targets", validate_canonical_targets()),
        ("coherencia targets/registry/target_policies", validate_targets_coherence()),
        ("consistencia documental mínima", validate_minimal_doc_consistency()),
        (
            "gate de cambios en compatibility_matrix",
            validate_matrix_change_requires_contract_updates(changed_files),
        ),
    )

    for stage, errors in checks:
        if errors:
            print("❌ Audit gate de targets: FALLÓ", file=sys.stderr)
            print(f" - etapa: {stage}", file=sys.stderr)
            for error in errors[:5]:
                print(f" - {error}", file=sys.stderr)
            if len(errors) > 5:
                print(f" - y {len(errors) - 5} error(es) adicional(es)", file=sys.stderr)
            return 1

    print("✅ Audit gate de targets: OK")
    print(f"   OFFICIAL_TARGETS: {', '.join(OFFICIAL_TARGETS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
