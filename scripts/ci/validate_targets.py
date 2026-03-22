#!/usr/bin/env python3
"""Validaciones CI simplificadas para el contrato final de 8 backends."""

from __future__ import annotations

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
from pcobra.cobra.transpilers.registry import TRANSPILER_CLASS_PATHS, official_transpiler_targets
from pcobra.cobra.transpilers.reverse import REVERSE_SCOPE_LANGUAGES
from pcobra.cobra.transpilers.targets import OFFICIAL_TARGETS, TIER1_TARGETS, TIER2_TARGETS
from scripts.targets_policy_common import FORBIDDEN_PUBLIC_TARGET_ALIASES, PUBLIC_TEXT_PATHS
from scripts.validate_targets_policy import _find_public_alias_errors

TRANSPILER_DIR = ROOT / "src/pcobra/cobra/transpilers/transpiler"
REVERSE_DIR = ROOT / "src/pcobra/cobra/transpilers/reverse"
GOLDEN_DIR = ROOT / "tests/integration/transpilers/golden"
ALLOWED_HISTORICAL_PATH_PREFIXES = (
    "docs/experimental/",
    "archive/retired_targets/",
)



def validate_registry_tables() -> list[str]:
    errors: list[str] = []
    expected = tuple(OFFICIAL_TARGETS)
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
    return errors



def validate_targeted_artifact_roots(
    official_targets: tuple[str, ...],
    reverse_scope: tuple[str, ...],
) -> list[str]:
    errors: list[str] = []

    expected_forward = {f"to_{target}.py" for target in official_targets if target != "javascript"}
    expected_forward.add("to_js.py")
    found_forward = {path.name for path in TRANSPILER_DIR.glob("to_*.py")}
    extra_forward = sorted(found_forward - expected_forward)
    missing_forward = sorted(expected_forward - found_forward)
    if extra_forward or missing_forward:
        errors.append(
            "Módulos to_*.py desalineados con OFFICIAL_TARGETS -> "
            f"missing={missing_forward}, extra={extra_forward}"
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

    expected_golden = {f"{target}.golden" for target in official_targets}
    found_golden = {path.name for path in GOLDEN_DIR.glob("*.golden")}
    extra_golden = sorted(found_golden - expected_golden)
    missing_golden = sorted(expected_golden - found_golden)
    if extra_golden or missing_golden:
        errors.append(
            "Golden files desalineados con OFFICIAL_TARGETS -> "
            f"missing={missing_golden}, extra={extra_golden}"
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
    expected = tuple(OFFICIAL_TARGETS)
    if tuple(official_targets) != expected:
        errors.append(
            "El conjunto recibido por validate_python_policy_literals no coincide con OFFICIAL_TARGETS -> "
            f"received={tuple(official_targets)}, official={expected}"
        )
    return errors



def main() -> int:
    official_targets = tuple(OFFICIAL_TARGETS)
    reverse_scope = tuple(REVERSE_SCOPE_LANGUAGES)
    errors = []
    errors.extend(validate_registry_tables())
    errors.extend(validate_targeted_artifact_roots(official_targets, reverse_scope))
    errors.extend(validate_scan_roots(official_targets, reverse_scope))
    errors.extend(validate_python_policy_literals(official_targets))

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
