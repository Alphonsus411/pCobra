from __future__ import annotations

import json

from cobra.cli.cli import main
from cobra.cli.commands import qa_validar_cmd as cmd_module
from pcobra.cobra.cli.commands import qa_validar_cmd as pcobra_cmd_module
from pcobra.cobra.qa.syntax_validation import SyntaxReport, SyntaxValidationExecution, TargetSummary, ValidationResult


def _execution() -> SyntaxValidationExecution:
    return SyntaxValidationExecution(
        report=SyntaxReport(
            python=ValidationResult("ok", "py"),
            cobra=ValidationResult("ok", "cobra"),
            targets={"python": TargetSummary(ok=1, fail=0, skipped=0)},
            strict=False,
            errors_by_target={},
        ),
        profile="completo",
        targets_requested=["python"],
        has_failures=False,
    )


def test_cli_qa_validar_exporta_feature_gap_report_json_estable(monkeypatch, tmp_path):
    output = tmp_path / "feature_gaps.json"

    monkeypatch.setattr(cmd_module, "execute_syntax_validation", lambda **_: _execution())
    monkeypatch.setattr(pcobra_cmd_module, "execute_syntax_validation", lambda **_: _execution())
    monkeypatch.setattr(cmd_module.VerifyCommand, "run", lambda *_: 0)
    monkeypatch.setattr(pcobra_cmd_module.VerifyCommand, "run", lambda *_: 0)

    fake_report = {
        "python": [],
        "javascript": [
            {
                "feature": "decoradores",
                "expected_level": "full",
                "actual_level": "partial",
                "missing_nodes": ["visit_decorador"],
            }
        ],
    }
    monkeypatch.setattr(cmd_module, "build_feature_gap_report", lambda: fake_report)
    monkeypatch.setattr(pcobra_cmd_module, "build_feature_gap_report", lambda: fake_report)

    rc = main(
        [
            "--modo",
            "mixto",
            "qa-validar",
            "--scope",
            "syntax",
            "--targets",
            "python",
            "--feature-gap-report",
            str(output),
            "--feature-gap-format",
            "json",
        ]
    )

    assert rc == 0
    payload = json.loads(output.read_text(encoding="utf-8"))
    assert payload == fake_report
