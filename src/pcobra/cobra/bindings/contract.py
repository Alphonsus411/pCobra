"""Compatibilidad del contrato de bindings dentro del namespace ``pcobra``.

Fuente canónica: ``bindings/contract.py``.
"""

from bindings.contract import (  # re-export canónico
    ABI_POLICY_BY_ROUTE,
    BINDINGS_BY_LANGUAGE,
    ROUTE_OPERATIONAL_LIMITS,
    AbiCompatibilityPolicy,
    BindingCapabilities,
    BindingRoute,
    JAVASCRIPT_BINDING,
    PYTHON_BINDING,
    RUST_BINDING,
    resolve_binding,
)

__all__ = [
    "AbiCompatibilityPolicy",
    "BindingCapabilities",
    "BindingRoute",
    "BINDINGS_BY_LANGUAGE",
    "ABI_POLICY_BY_ROUTE",
    "ROUTE_OPERATIONAL_LIMITS",
    "PYTHON_BINDING",
    "JAVASCRIPT_BINDING",
    "RUST_BINDING",
    "resolve_binding",
]
