#!/usr/bin/env python3
"""Valida de forma estricta la política final de 8 backends oficiales."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from pcobra.cobra.transpilers.reverse import REVERSE_SCOPE_LANGUAGES
from scripts.ci.validate_targets import (
    validate_final_backend_repo_audit,
    validate_operational_checklist,
    validate_public_documentation_alignment,
    validate_python_policy_literals,
    validate_registry_tables,
    validate_scan_roots,
    validate_targeted_artifact_roots,
)
from scripts.lint_policy_drift import main as lint_policy_drift_main
from scripts.targets_policy_common import VALIDATION_SCAN_PATHS, read_target_policy

SCAN_ROOTS = tuple(path.relative_to(ROOT).as_posix() for path in VALIDATION_SCAN_PATHS)
GENERATED_PATH_PARTS = {
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    "site",
    "build",
    "dist",
    "docs/_build",
}


def iter_scan_files(root: Path) -> list[Path]:
    """Compatibilidad histórica: devuelve ficheros vigilados saltando cachés/generados."""
    files: list[Path] = []
    for entry in SCAN_ROOTS:
        path = root / entry
        if not path.exists():
            continue
        if path.is_file():
            rel = path.relative_to(root).as_posix()
            if any(part in rel for part in GENERATED_PATH_PARTS):
                continue
            files.append(path)
            continue
        for candidate in path.rglob("*"):
            if not candidate.is_file():
                continue
            rel = candidate.relative_to(root).as_posix()
            if any(part in rel for part in GENERATED_PATH_PARTS):
                continue
            files.append(candidate)
    return files


def _run_stage(name: str, errors: list[str]) -> int | None:
    if not errors:
        return None
    print("❌ Validación de política de targets: FALLÓ", file=sys.stderr)
    print(f" - etapa: {name}", file=sys.stderr)
    print(f" - {errors[0]}", file=sys.stderr)
    if len(errors) > 1:
        print(
            f" - y {len(errors) - 1} desalineación(es) adicional(es) en la misma etapa",
            file=sys.stderr,
        )
    return 1


def main() -> int:
    policy = read_target_policy()
    tier1_targets = tuple(policy["tier1_targets"])
    tier2_targets = tuple(policy["tier2_targets"])
    official_targets = tuple(policy["official_targets"])
    reverse_scope = tuple(REVERSE_SCOPE_LANGUAGES)

    if official_targets != tier1_targets + tier2_targets:
        print("❌ Validación de política de targets: FALLÓ", file=sys.stderr)
        print(
            " - src/pcobra/cobra/transpilers/targets.py: OFFICIAL_TARGETS debe ser exactamente TIER1_TARGETS + TIER2_TARGETS -> "
            f"official={official_targets}, tier1={tier1_targets}, tier2={tier2_targets}",
            file=sys.stderr,
        )
        return 1

    if tuple(policy["public_names"]) != official_targets:
        print("❌ Validación de política de targets: FALLÓ", file=sys.stderr)
        print(
            " - scripts/targets_policy_common.py: public_names debe coincidir exactamente con OFFICIAL_TARGETS -> "
            f"public={tuple(policy['public_names'])}, official={official_targets}",
            file=sys.stderr,
        )
        return 1

    if tuple(policy["internal_names"]) != official_targets:
        print("❌ Validación de política de targets: FALLÓ", file=sys.stderr)
        print(
            " - scripts/targets_policy_common.py: internal_names debe coincidir exactamente con OFFICIAL_TARGETS -> "
            f"internal={tuple(policy['internal_names'])}, official={official_targets}",
            file=sys.stderr,
        )
        return 1

    stages = (
        ("registros canónicos", validate_registry_tables()),
        ("checklist operativo", validate_operational_checklist(official_targets)),
        (
            "artefactos dirigidos",
            validate_targeted_artifact_roots(official_targets, reverse_scope),
        ),
        ("escaneo público", validate_scan_roots(official_targets, reverse_scope)),
        (
            "documentación pública",
            validate_public_documentation_alignment(official_targets, reverse_scope),
        ),
        (
            "contrato Python/Holobit/SDK",
            validate_python_policy_literals(official_targets),
        ),
        ("auditoría de repo", validate_final_backend_repo_audit()),
        (
            "policy drift en rutas públicas",
            [] if lint_policy_drift_main() == 0 else ["scripts/lint_policy_drift.py reportó drift"],
        ),
    )
    for stage_name, errors in stages:
        result = _run_stage(stage_name, errors)
        if result is not None:
            return result

    print("✅ Validación de política de targets: OK")
    print(f"   Tier 1: {', '.join(tier1_targets)}")
    print(f"   Tier 2: {', '.join(tier2_targets)}")
    print(f"   OFFICIAL_TARGETS: {', '.join(official_targets)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
