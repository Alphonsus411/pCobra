#!/usr/bin/env python3
"""Validaciones CI simplificadas para el contrato final de 8 backends."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC_ROOT = ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from pcobra.cobra.cli.commands.benchmarks_cmd import BACKENDS as BENCHMARKS_BACKENDS
from pcobra.cobra.cli.commands.compile_cmd import LANG_CHOICES, TRANSPILERS
from pcobra.cobra.transpilers.registry import (
    TRANSPILER_CLASS_PATHS,
    official_transpiler_registry_literal,
    official_transpiler_targets,
)
from pcobra.cobra.transpilers.reverse import REVERSE_SCOPE_LANGUAGES
from pcobra.cobra.transpilers.targets import OFFICIAL_TARGETS, TIER1_TARGETS, TIER2_TARGETS
from scripts.targets_policy_common import FORBIDDEN_PUBLIC_TARGET_ALIASES, PUBLIC_TEXT_PATHS
from scripts.validate_targets_policy import _find_public_alias_errors

FINAL_OFFICIAL_TARGETS = (
    "python",
    "rust",
    "javascript",
    "wasm",
    "go",
    "cpp",
    "java",
    "asm",
)
EXPECTED_TRANSPILER_MODULES = (
    "src/pcobra/cobra/transpilers/transpiler/to_python.py",
    "src/pcobra/cobra/transpilers/transpiler/to_rust.py",
    "src/pcobra/cobra/transpilers/transpiler/to_js.py",
    "src/pcobra/cobra/transpilers/transpiler/to_wasm.py",
    "src/pcobra/cobra/transpilers/transpiler/to_go.py",
    "src/pcobra/cobra/transpilers/transpiler/to_cpp.py",
    "src/pcobra/cobra/transpilers/transpiler/to_java.py",
    "src/pcobra/cobra/transpilers/transpiler/to_asm.py",
)
EXPECTED_GOLDEN_FILES = (
    "tests/integration/transpilers/golden/python.golden",
    "tests/integration/transpilers/golden/rust.golden",
    "tests/integration/transpilers/golden/javascript.golden",
    "tests/integration/transpilers/golden/wasm.golden",
    "tests/integration/transpilers/golden/go.golden",
    "tests/integration/transpilers/golden/cpp.golden",
    "tests/integration/transpilers/golden/java.golden",
    "tests/integration/transpilers/golden/asm.golden",
)
EXPECTED_TRANSPILER_REGISTRY = {
    "python": ("pcobra.cobra.transpilers.transpiler.to_python", "TranspiladorPython"),
    "rust": ("pcobra.cobra.transpilers.transpiler.to_rust", "TranspiladorRust"),
    "javascript": ("pcobra.cobra.transpilers.transpiler.to_js", "TranspiladorJavaScript"),
    "wasm": ("pcobra.cobra.transpilers.transpiler.to_wasm", "TranspiladorWasm"),
    "go": ("pcobra.cobra.transpilers.transpiler.to_go", "TranspiladorGo"),
    "cpp": ("pcobra.cobra.transpilers.transpiler.to_cpp", "TranspiladorCPP"),
    "java": ("pcobra.cobra.transpilers.transpiler.to_java", "TranspiladorJava"),
    "asm": ("pcobra.cobra.transpilers.transpiler.to_asm", "TranspiladorASM"),
}

TRANSPILER_DIR = ROOT / "src/pcobra/cobra/transpilers/transpiler"
REVERSE_DIR = ROOT / "src/pcobra/cobra/transpilers/reverse"
GOLDEN_DIR = ROOT / "tests/integration/transpilers/golden"
ALLOWED_HISTORICAL_PATH_PREFIXES = (
    "docs/historico/",
    "docs/experimental/",
    "archive/retired_targets/",
)
REPO_AUDIT_ALLOWED_PATH_PREFIXES = ALLOWED_HISTORICAL_PATH_PREFIXES
REPO_AUDIT_SCAN_ROOTS = ("src", "docs", "tests", "scripts")
REPO_AUDIT_ALLOWED_FILE_PATHS = frozenset(
    {
        "scripts/lint_legacy_aliases.py",
        "scripts/targets_policy_common.py",
        "scripts/validate_targets_policy.py",
        "scripts/ci/validate_targets.py",
        "tests/unit/test_cli_target_aliases.py",
        "tests/unit/test_public_docs_scope.py",
        "tests/unit/test_validate_targets_policy_script.py",
        "tests/unit/test_reverse_transpilers_registry.py",
        "tests/unit/test_verify_cmd.py",
        "tests/unit/test_cli_compilar_tipos.py",
        "tests/performance/test_transpile_time.py",
        "scripts/benchmarks/targets_policy.py",
        "docs/frontend/uml/arquitectura_general.puml",
    }
)
REPO_AUDIT_FORBIDDEN_TERMS: tuple[tuple[re.Pattern[str], str], ...] = (
    (re.compile(r"(?<![\w/-])hololang(?![\w/-])", re.IGNORECASE), "backend retirado 'hololang'"),
    (re.compile(r"(?<![\w/-])reverse[ -]wasm(?![\w/-])", re.IGNORECASE), "pipeline retirado 'reverse wasm'"),
    (re.compile(r"(?<![\w/-])llvm(?![\w/-])", re.IGNORECASE), "backend/pipeline retirado 'llvm'"),
    (re.compile(r"(?<![\w/-])latex(?![\w/-])", re.IGNORECASE), "backend/pipeline retirado 'latex'"),
)
REPO_AUDIT_FORBIDDEN_ALIAS_LITERALS: tuple[tuple[re.Pattern[str], str], ...] = tuple(
    (
        re.compile(r'(?P<quote>[\"\'])' + re.escape(alias) + r'(?P=quote)', re.IGNORECASE),
        alias,
    )
    for alias, _ in FORBIDDEN_PUBLIC_TARGET_ALIASES
)



def validate_registry_tables() -> list[str]:
    errors: list[str] = []
    expected = FINAL_OFFICIAL_TARGETS
    if tuple(OFFICIAL_TARGETS) != expected:
        errors.append(
            "OFFICIAL_TARGETS no coincide con el contrato final de ocho backends -> "
            f"official={tuple(OFFICIAL_TARGETS)}, expected={expected}"
        )
    if tuple(TIER1_TARGETS + TIER2_TARGETS) != expected:
        errors.append(
            "TIER1_TARGETS + TIER2_TARGETS no coincide con OFFICIAL_TARGETS -> "
            f"tier1+tier2={TIER1_TARGETS + TIER2_TARGETS}, official={expected}"
        )
    if tuple(TRANSPILER_CLASS_PATHS) != expected:
        errors.append(
            "TRANSPILER_CLASS_PATHS no coincide con OFFICIAL_TARGETS -> "
            f"registry={tuple(TRANSPILER_CLASS_PATHS)}, official={expected}"
        )
    if tuple(official_transpiler_targets()) != expected:
        errors.append(
            "official_transpiler_targets() no coincide con OFFICIAL_TARGETS -> "
            f"registry={official_transpiler_targets()}, official={expected}"
        )
    if tuple(TRANSPILERS) != expected:
        errors.append(
            "TRANSPILERS no coincide con OFFICIAL_TARGETS -> "
            f"transpilers={tuple(TRANSPILERS)}, official={expected}"
        )
    if tuple(LANG_CHOICES) != expected:
        errors.append(
            "LANG_CHOICES no coincide con OFFICIAL_TARGETS -> "
            f"choices={tuple(LANG_CHOICES)}, official={expected}"
        )
    if tuple(BENCHMARKS_BACKENDS) != expected:
        errors.append(
            "BACKENDS de benchmarks no coincide con OFFICIAL_TARGETS -> "
            f"benchmarks={tuple(BENCHMARKS_BACKENDS)}, official={expected}"
        )
    if official_transpiler_registry_literal() != EXPECTED_TRANSPILER_REGISTRY:
        errors.append(
            "El literal del registro canónico no coincide con los ocho transpilers finales -> "
            f"registry={official_transpiler_registry_literal()}, expected={EXPECTED_TRANSPILER_REGISTRY}"
        )
    return errors



def validate_targeted_artifact_roots(
    official_targets: tuple[str, ...],
    reverse_scope: tuple[str, ...],
) -> list[str]:
    errors: list[str] = []

    if tuple(official_targets) != FINAL_OFFICIAL_TARGETS:
        errors.append(
            "validate_targeted_artifact_roots recibió un conjunto distinto al contrato final -> "
            f"received={tuple(official_targets)}, expected={FINAL_OFFICIAL_TARGETS}"
        )

    found_forward_paths = {path.relative_to(ROOT).as_posix() for path in ROOT.rglob("to_*.py")}
    expected_forward_paths = set(EXPECTED_TRANSPILER_MODULES)
    extra_forward = sorted(found_forward_paths - expected_forward_paths)
    missing_forward = sorted(expected_forward_paths - found_forward_paths)
    if extra_forward or missing_forward:
        errors.append(
            "Módulos to_*.py desalineados con el contrato final -> "
            f"missing={missing_forward}, extra={extra_forward}"
        )
    found_forward = {path.name for path in TRANSPILER_DIR.glob("to_*.py")}
    expected_forward = {Path(path).name for path in EXPECTED_TRANSPILER_MODULES}
    if found_forward != expected_forward:
        errors.append(
            "El directorio canónico de transpilers no coincide exactamente con los ocho módulos esperados -> "
            f"found={sorted(found_forward)}, expected={sorted(expected_forward)}"
        )

    expected_reverse = {f"from_{target}.py" for target in reverse_scope if target != "javascript"}
    expected_reverse.add("from_js.py")
    found_reverse = {path.name for path in REVERSE_DIR.glob("from_*.py")}
    extra_reverse = sorted(found_reverse - expected_reverse)
    missing_reverse = sorted(expected_reverse - found_reverse)
    if extra_reverse or missing_reverse:
        errors.append(
            "Módulos from_*.py desalineados con REVERSE_SCOPE_LANGUAGES -> "
            f"missing={missing_reverse}, extra={extra_reverse}"
        )

    found_golden_paths = {path.relative_to(ROOT).as_posix() for path in ROOT.rglob("*.golden")}
    expected_golden_paths = set(EXPECTED_GOLDEN_FILES)
    extra_golden = sorted(found_golden_paths - expected_golden_paths)
    missing_golden = sorted(expected_golden_paths - found_golden_paths)
    if extra_golden or missing_golden:
        errors.append(
            "Golden files desalineados con el contrato final -> "
            f"missing={missing_golden}, extra={extra_golden}"
        )
    found_golden = {path.name for path in GOLDEN_DIR.glob("*.golden")}
    expected_golden = {Path(path).name for path in EXPECTED_GOLDEN_FILES}
    if found_golden != expected_golden:
        errors.append(
            "El directorio canónico de goldens no coincide exactamente con los ocho artefactos esperados -> "
            f"found={sorted(found_golden)}, expected={sorted(expected_golden)}"
        )

    return errors



def validate_scan_roots(
    official_targets: tuple[str, ...],
    reverse_scope: tuple[str, ...],
) -> list[str]:
    del official_targets, reverse_scope
    errors: list[str] = []
    for path in PUBLIC_TEXT_PATHS:
        if not path.exists():
            errors.append(f"Ruta pública vigilada inexistente: {path.relative_to(ROOT).as_posix()}")
            continue
        content = path.read_text(encoding="utf-8", errors="ignore")
        rel = path.relative_to(ROOT).as_posix()
        errors.extend(_find_public_alias_errors(rel, content))
    return errors



def validate_python_policy_literals(
    official_targets: tuple[str, ...],
    **_: tuple[str, ...],
) -> list[str]:
    errors: list[str] = []
    expected = FINAL_OFFICIAL_TARGETS
    if tuple(official_targets) != expected:
        errors.append(
            "El conjunto recibido por validate_python_policy_literals no coincide con el contrato final -> "
            f"received={tuple(official_targets)}, expected={expected}"
        )
    return errors



def _iter_repo_audit_files() -> list[Path]:
    files: list[Path] = []
    for root_name in REPO_AUDIT_SCAN_ROOTS:
        base = ROOT / root_name
        if not base.exists():
            continue
        files.extend(path for path in base.rglob("*") if path.is_file())
    return files



def _is_historical_repo_path(rel: str) -> bool:
    return rel in REPO_AUDIT_ALLOWED_FILE_PATHS or rel.startswith(REPO_AUDIT_ALLOWED_PATH_PREFIXES)



def validate_final_backend_repo_audit() -> list[str]:
    errors: list[str] = []
    for path in _iter_repo_audit_files():
        rel = path.relative_to(ROOT).as_posix()
        if _is_historical_repo_path(rel):
            continue
        try:
            content = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for pattern, description in REPO_AUDIT_FORBIDDEN_TERMS:
            for match in pattern.finditer(content):
                line_no = content.count("\n", 0, match.start()) + 1
                errors.append(f"{rel}:{line_no}: referencia fuera del conjunto final -> {description}")
        for pattern, alias in REPO_AUDIT_FORBIDDEN_ALIAS_LITERALS:
            for match in pattern.finditer(content):
                line_no = content.count("\n", 0, match.start()) + 1
                errors.append(f"{rel}:{line_no}: alias legacy literal fuera del conjunto final -> {alias}")
    return errors



def main() -> int:
    official_targets = tuple(OFFICIAL_TARGETS)
    reverse_scope = tuple(REVERSE_SCOPE_LANGUAGES)
    errors = []
    errors.extend(validate_registry_tables())
    errors.extend(validate_targeted_artifact_roots(official_targets, reverse_scope))
    errors.extend(validate_scan_roots(official_targets, reverse_scope))
    errors.extend(validate_python_policy_literals(official_targets))
    errors.extend(validate_final_backend_repo_audit())

    if errors:
        print("❌ Validación CI de targets: FALLÓ", file=sys.stderr)
        for error in errors:
            print(f" - {error}", file=sys.stderr)
        return 1

    print("✅ Validación CI de targets: OK")
    print(f"   OFFICIAL_TARGETS: {', '.join(official_targets)}")
    print(f"   REVERSE_SCOPE_LANGUAGES: {', '.join(reverse_scope)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
