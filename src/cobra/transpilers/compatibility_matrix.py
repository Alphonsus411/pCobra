"""Shim histórico para ``cobra.transpilers.compatibility_matrix``.

Fuente canónica: :mod:`pcobra.cobra.transpilers.compatibility_matrix`.
"""

from pcobra.cobra.transpilers.compatibility_matrix import (
    BACKEND_COMPATIBILITY,
    CONTRACT_FEATURES,
    SDK_FULL_BACKENDS,
    SDK_PARTIAL_BACKENDS,
    VALID_COMPATIBILITY_LEVELS,
    VALID_TIERS,
    validate_backend_compatibility_contract,
)

__all__ = [
    "CONTRACT_FEATURES",
    "VALID_COMPATIBILITY_LEVELS",
    "VALID_TIERS",
    "SDK_FULL_BACKENDS",
    "SDK_PARTIAL_BACKENDS",
    "BACKEND_COMPATIBILITY",
    "validate_backend_compatibility_contract",
]
