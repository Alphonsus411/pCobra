#!/usr/bin/env python3
"""Gate CI para contrato JSON de `cobra validar-sintaxis --report-json`."""

from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from pcobra.cobra.qa.syntax_validation import (
    SYNTAX_REPORT_SCHEMA_VERSION,
    SyntaxReport,
    SyntaxValidationExecution,
    TargetSummary,
    ValidationResult,
    build_syntax_report_payload,
)

SNAPSHOT_PATH = Path("tests/data/snapshots/validar_sintaxis_report_schema_v1.json")
DOCS_PATHS = [Path("README.md"), Path("docs/tareas_validacion_sintaxis.md")]


def _shape(value):
    if isinstance(value, dict):
        return {k: _shape(v) for k, v in sorted(value.items())}
    if isinstance(value, list):
        return [_shape(v) for v in value]
    return type(value).__name__


def _build_payload() -> dict:
    execution = SyntaxValidationExecution(
        report=SyntaxReport(
            python=ValidationResult("ok", "Sintaxis Python correcta en src/ y tests/"),
            cobra=ValidationResult("ok", "Parse básico Cobra correcto"),
            targets={"python": TargetSummary(ok=1, fail=0, skipped=0)},
            strict=False,
            errors_by_target={},
        ),
        profile="completo",
        targets_requested=["python"],
        has_failures=False,
    )
    payload = build_syntax_report_payload(execution)
    payload["timestamp"] = "2026-01-01T00:00:00+00:00"
    payload["python"]["version"] = "3.11.0"
    payload["python_runtime"] = "3.11.0"
    payload["cobra"]["version"] = "dev"
    return payload


def main() -> int:
    snapshot = json.loads(SNAPSHOT_PATH.read_text(encoding="utf-8"))
    payload = _build_payload()

    if payload["schema_version"] != SYNTAX_REPORT_SCHEMA_VERSION:
        raise SystemExit("schema_version del payload no coincide con constante interna")

    if _shape(payload) != _shape(snapshot):
        raise SystemExit(
            "El contrato JSON de validar-sintaxis cambió: actualiza snapshot y documentación asociada."
        )

    marker = f"schema_version={SYNTAX_REPORT_SCHEMA_VERSION}"
    missing = [str(path) for path in DOCS_PATHS if marker not in path.read_text(encoding="utf-8")]
    if missing:
        raise SystemExit(
            "Falta documentar la versión del contrato JSON en: " + ", ".join(missing)
        )

    print("Contrato JSON de validar-sintaxis OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
