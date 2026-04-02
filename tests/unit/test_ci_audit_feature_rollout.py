from __future__ import annotations

from scripts.ci.audit_feature_rollout import audit_feature_id, validate_rollout_gate


def test_rollout_gate_requires_test_and_docs_for_parser_or_stdlib_changes() -> None:
    changed = {"src/pcobra/standard_library/texto.py"}
    errors = validate_rollout_gate(changed)
    assert len(errors) == 2
    assert "pruebas" in errors[0]
    assert "documental/matriz" in errors[1]


def test_rollout_gate_accepts_when_test_and_docs_exist() -> None:
    changed = {
        "src/pcobra/core/parser.py",
        "tests/unit/test_parser_ast.py",
        "docs/matriz_transpiladores.md",
    }
    assert validate_rollout_gate(changed) == []


def test_feature_audit_detects_bootstrap_example_fixture() -> None:
    evidence = audit_feature_id("feature_base")
    assert evidence["examples"]
