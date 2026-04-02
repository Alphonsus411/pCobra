#!/usr/bin/env python3
"""Smoke de transpiladores oficiales usando la API canónica de sintaxis."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = ROOT / "src"


def main() -> int:
    sys.path.insert(0, str(SRC_DIR))

    from pcobra.cobra.qa.syntax_validation import execute_syntax_validation
    from pcobra.cobra.transpilers.registry import build_official_transpilers, official_transpiler_targets

    ordered_targets = official_transpiler_targets()

    print("🔎 Smoke de sintaxis de transpiladores oficiales vía API unificada")
    print(f"   Targets: {', '.join(ordered_targets)}")

    execution = execute_syntax_validation(
        profile="transpiladores",
        targets_raw=",".join(ordered_targets),
        strict=False,
        transpilers=build_official_transpilers(),
    )

    print("\n📊 Resumen por target")
    for target in ordered_targets:
        summary = execution.report.targets[target]
        print(f" - {target}: ok={summary.ok} fail={summary.fail} skipped={summary.skipped}")

    if execution.has_failures:
        print("\n🚨 Smoke de transpiladores con fallos en targets oficiales.")
        return 1

    print("\n🎉 Smoke de transpiladores completado sin fallos obligatorios.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
