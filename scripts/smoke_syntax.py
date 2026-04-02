#!/usr/bin/env python3
"""Smoke check rápido usando la API canónica de validación de sintaxis."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = ROOT / "src"


def main() -> int:
    sys.path.insert(0, str(SRC_DIR))

    from pcobra.cobra.qa.syntax_validation import execute_syntax_validation
    from pcobra.cobra.transpilers.registry import build_official_transpilers

    print("🔎 Ejecutando smoke de sintaxis vía API unificada (perfil=solo-cobra)")
    execution = execute_syntax_validation(
        profile="solo-cobra",
        targets_raw="",
        strict=False,
        transpilers=build_official_transpilers(),
    )

    print(f" - Python: {execution.report.python.status} ({execution.report.python.message})")
    print(f" - Cobra: {execution.report.cobra.status} ({execution.report.cobra.message})")

    if execution.has_failures:
        print("🚨 Smoke de sintaxis con errores.")
        return 1

    print("🎉 Smoke de sintaxis completado correctamente.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
