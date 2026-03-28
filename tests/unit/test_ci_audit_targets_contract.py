from __future__ import annotations

from scripts.ci.audit_targets_contract import (
    MIN_DOC_PATHS_FOR_MATRIX_CHANGE,
    CONTRACT_TEST_HINTS,
    validate_canonical_targets,
    validate_matrix_change_requires_contract_updates,
    validate_targets_coherence,
)


def test_canonical_targets_are_valid_in_repo_state() -> None:
    assert validate_canonical_targets() == []


def test_targets_coherence_is_valid_in_repo_state() -> None:
    assert validate_targets_coherence() == []


def test_matrix_change_requires_docs_and_tests_updates() -> None:
    changed = {"src/pcobra/cobra/transpilers/compatibility_matrix.py"}
    errors = validate_matrix_change_requires_contract_updates(changed)
    assert len(errors) == 2
    assert "documentación contractual" in errors[0]
    assert "tests de contrato" in errors[1]


def test_matrix_change_accepts_when_docs_and_tests_are_updated() -> None:
    changed = {
        "src/pcobra/cobra/transpilers/compatibility_matrix.py",
        MIN_DOC_PATHS_FOR_MATRIX_CHANGE[0],
        CONTRACT_TEST_HINTS[0],
    }
    assert validate_matrix_change_requires_contract_updates(changed) == []
