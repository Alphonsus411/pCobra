from __future__ import annotations

import json
from pathlib import Path

from pcobra.cobra.qa.syntax_validation import (
    SYNTAX_REPORT_SCHEMA_VERSION,
    SyntaxReport,
    SyntaxValidationExecution,
    TargetSummary,
    ValidationResult,
    build_syntax_report_payload,
)

SNAPSHOT_PATH = Path("tests/data/snapshots/validar_sintaxis_report_schema_v1.json")


def _shape(value):
    if isinstance(value, dict):
        return {k: _shape(v) for k, v in sorted(value.items())}
    if isinstance(value, list):
        return [_shape(v) for v in value]
    return type(value).__name__


def test_validar_sintaxis_report_schema_snapshot_contract():
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

    snapshot = json.loads(SNAPSHOT_PATH.read_text(encoding="utf-8"))

    assert payload["schema_version"] == SYNTAX_REPORT_SCHEMA_VERSION
    assert _shape(payload) == _shape(snapshot)
    assert sorted(payload.keys()) == sorted(snapshot.keys())
