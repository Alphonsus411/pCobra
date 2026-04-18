"""Compatibilidad del contrato de bindings dentro del namespace ``pcobra``.

Fuente canónica: ``bindings/contract.py``.
"""

from bindings.contract import (  # re-export canónico
    ABI_POLICY_BY_ROUTE,
    BINDINGS_BY_LANGUAGE,
    OFFICIAL_PUBLIC_LANGUAGES,
    OFFICIAL_PUBLIC_ROUTE_MATRIX,
    ROUTE_OPERATIONAL_LIMITS,
    AbiCompatibilityPolicy,
    BindingCapabilities,
    BindingRoute,
    JAVASCRIPT_BINDING,
    PYTHON_BINDING,
    RUST_BINDING,
    route_matrix_markdown,
    validate_public_language,
    resolve_binding,
)

__all__ = [
    "AbiCompatibilityPolicy",
    "BindingCapabilities",
    "BindingRoute",
    "BINDINGS_BY_LANGUAGE",
    "OFFICIAL_PUBLIC_LANGUAGES",
    "OFFICIAL_PUBLIC_ROUTE_MATRIX",
    "ABI_POLICY_BY_ROUTE",
    "ROUTE_OPERATIONAL_LIMITS",
    "PYTHON_BINDING",
    "JAVASCRIPT_BINDING",
    "RUST_BINDING",
    "route_matrix_markdown",
    "validate_public_language",
    "resolve_binding",
]
