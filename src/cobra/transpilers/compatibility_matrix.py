"""Shim histórico para ``cobra.transpilers.compatibility_matrix``.

Fuente canónica: :mod:`pcobra.cobra.transpilers.compatibility_matrix`.
"""

from pcobra.cobra.transpilers.compatibility_matrix import (
    AST_FEATURE_EVIDENCE_BASELINE,
    AST_FEATURE_EVIDENCE_SOURCE,
    AST_FEATURE_MINIMUM_CONTRACT,
    AST_FEATURES,
    BACKEND_COMPATIBILITY,
    BEST_EFFORT_RUNTIME_BACKENDS,
    CONTRACT_FEATURES,
    OFFICIAL_RUNTIME_BACKENDS,
    SDK_FULL_BACKENDS,
    SDK_PARTIAL_BACKENDS,
    TRANSPILATION_ONLY_BACKENDS,
    VALID_COMPATIBILITY_LEVELS,
    VALID_TIERS,
    build_feature_gap_report,
    validate_ast_feature_parity_release_gate,
    validate_backend_compatibility_contract,
)

__all__ = [
    "CONTRACT_FEATURES",
    "VALID_COMPATIBILITY_LEVELS",
    "VALID_TIERS",
    "SDK_FULL_BACKENDS",
    "SDK_PARTIAL_BACKENDS",
    "OFFICIAL_RUNTIME_BACKENDS",
    "BEST_EFFORT_RUNTIME_BACKENDS",
    "TRANSPILATION_ONLY_BACKENDS",
    "AST_FEATURES",
    "AST_FEATURE_MINIMUM_CONTRACT",
    "AST_FEATURE_EVIDENCE_BASELINE",
    "AST_FEATURE_EVIDENCE_SOURCE",
    "BACKEND_COMPATIBILITY",
    "build_feature_gap_report",
    "validate_ast_feature_parity_release_gate",
    "validate_backend_compatibility_contract",
]
