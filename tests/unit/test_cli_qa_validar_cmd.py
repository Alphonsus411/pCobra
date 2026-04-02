from __future__ import annotations

import json
from argparse import Namespace
from pathlib import Path

from cobra.cli.commands import qa_validar_cmd as cmd_module
from cobra.cli.commands.qa_validar_cmd import QaValidarCommand
from pcobra.cobra.qa.syntax_validation import SyntaxReport, SyntaxValidationExecution, TargetSummary, ValidationResult


def _args(**kwargs) -> Namespace:
    base = {
        "modo": "mixto",
        "archivo": "programa.co",
        "strict": False,
        "solo_cobra": False,
        "targets": "",
        "scope": "all",
        "report_json": None,
        "feature_gap_report": None,
        "feature_gap_format": "json",
    }
    base.update(kwargs)
    return Namespace(**base)


def _execution(has_failures: bool = False) -> SyntaxValidationExecution:
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
        has_failures=has_failures,
    )


def test_qa_validar_exit_code_0_cuando_todo_ok(monkeypatch):
    command = QaValidarCommand()

    monkeypatch.setattr(cmd_module, "execute_syntax_validation", lambda **_: _execution(False))
    monkeypatch.setattr(cmd_module.VerifyCommand, "run", lambda *_: 0)

    rc = command.run(_args(targets="python,javascript"))

    assert rc == 0


def test_qa_validar_exit_code_1_si_falla_runtime(monkeypatch):
    command = QaValidarCommand()

    monkeypatch.setattr(cmd_module, "execute_syntax_validation", lambda **_: _execution(False))
    monkeypatch.setattr(cmd_module.VerifyCommand, "run", lambda *_: 1)

    rc = command.run(_args(targets="python"))

    assert rc == 1


def test_qa_validar_propaga_errores_en_orquestacion(monkeypatch):
    command = QaValidarCommand()
    monkeypatch.setattr(cmd_module, "execute_syntax_validation", lambda **_: _execution(False))
    monkeypatch.setattr(
        cmd_module.VerifyCommand,
        "run",
        lambda *_: (_ for _ in ()).throw(RuntimeError("fallo runtime interno")),
    )

    rc = command.run(_args(targets="python"))

    assert rc == 1


def test_qa_validar_strict_falla_si_no_hay_runtime_ejecutable(monkeypatch):
    command = QaValidarCommand()

    monkeypatch.setattr(cmd_module, "execute_syntax_validation", lambda **_: _execution(False))

    rc = command.run(_args(strict=True, targets="wasm", scope="runtime"))

    assert rc == 1


def test_qa_validar_reporte_json_agregado(monkeypatch, tmp_path: Path):
    command = QaValidarCommand()
    output = tmp_path / "qa.json"

    monkeypatch.setattr(cmd_module, "execute_syntax_validation", lambda **_: _execution(False))
    monkeypatch.setattr(cmd_module.VerifyCommand, "run", lambda *_: 0)

    rc = command.run(_args(targets="python", report_json=str(output)))

    assert rc == 0
    payload = json.loads(output.read_text(encoding="utf-8"))
    assert set(payload) == {"syntax", "transpilers", "runtime_equivalence"}


def test_qa_validar_exporta_feature_gap_report_markdown(monkeypatch, tmp_path: Path):
    command = QaValidarCommand()
    output = tmp_path / "feature-gaps.md"

    monkeypatch.setattr(cmd_module, "execute_syntax_validation", lambda **_: _execution(False))
    monkeypatch.setattr(cmd_module.VerifyCommand, "run", lambda *_: 0)
    monkeypatch.setattr(
        cmd_module,
        "build_feature_gap_report",
        lambda: {
            "python": [],
            "javascript": [
                {
                    "feature": "decoradores",
                    "expected_level": "full",
                    "actual_level": "partial",
                    "missing_nodes": ["visit_decorador"],
                }
            ],
        },
    )

    rc = command.run(_args(targets="python", feature_gap_report=str(output), feature_gap_format="markdown"))

    assert rc == 0
    content = output.read_text(encoding="utf-8")
    assert "## javascript" in content
    assert "| decoradores | full | partial | visit_decorador |" in content
