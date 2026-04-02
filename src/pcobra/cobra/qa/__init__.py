"""Utilidades QA para validaciones compartidas."""

from .syntax_validation import (
    SUPPORTED_VALIDATOR_TARGETS,
    SyntaxReport,
    TargetSummary,
    ValidationResult,
    VALIDATORS,
    _tokenize,
    load_ast_for_fixture,
    run_external_command,
    run_transpiler_syntax_validation,
)

__all__ = [
    "SUPPORTED_VALIDATOR_TARGETS",
    "SyntaxReport",
    "TargetSummary",
    "ValidationResult",
    "VALIDATORS",
    "_tokenize",
    "load_ast_for_fixture",
    "run_external_command",
    "run_transpiler_syntax_validation",
]
