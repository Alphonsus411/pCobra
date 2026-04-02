#!/usr/bin/env python3
"""Smoke de transpiladores oficiales + validación de sintaxis por backend."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = ROOT / "src"

COBRA_FIXTURES = [
    ROOT / "scripts" / "benchmarks" / "programs" / "smoke_assign.co",
    ROOT / "examples" / "smoke_assign.co",
]


def main() -> int:
    sys.path.insert(0, str(SRC_DIR))

    from pcobra.cobra.qa.syntax_validation import run_transpiler_syntax_validation
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

    report, events, has_failures = run_transpiler_syntax_validation(
        fixtures=fixtures,
        targets=ordered_targets,
        transpilers=transpilers,
        strict=False,
    )

    for event in events:
        fixture_path = Path(event["fixture"])
        try:
            label = fixture_path.relative_to(ROOT)
        except ValueError:
            label = fixture_path
        status = event["status"]
        icon = "✅" if status == "ok" else "⏭️" if status == "skipped" else "❌"
        print(f"{icon} [{event['target']}] ({label}) {event['message']}")

    print("\n📊 Resumen por target")
    for target in ordered_targets:
        summary = report.targets[target]
        print(f" - {target}: ok={summary.ok} fail={summary.fail} skipped={summary.skipped}")

    if has_failures:
        print("\n🚨 Smoke de transpiladores con fallos en targets oficiales.")
        return 1

    print("\n🎉 Smoke de transpiladores completado sin fallos obligatorios.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
