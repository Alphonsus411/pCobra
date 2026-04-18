"""Compatibilidad del contrato de bindings dentro del namespace ``pcobra``.

Fuente canónica: ``bindings/contract.py``.
"""

from bindings.contract import (  # re-export canónico
    ABI_POLICY_BY_ROUTE,
    BINDINGS_BY_LANGUAGE,
    COMMAND_EVENT_SCHEMA,
    EVENT_VALIDATION_FIELDS,
    OFFICIAL_PUBLIC_LANGUAGES,
    OFFICIAL_PUBLIC_ROUTE_MATRIX,
    PUBLIC_RUNTIME_COMMANDS,
    ROUTE_OPERATIONAL_LIMITS,
    AbiCompatibilityPolicy,
    BindingCapabilities,
    BindingRoute,
    JAVASCRIPT_BINDING,
    PYTHON_BINDING,
    RUST_BINDING,
    resolve_command_event,
    route_matrix_markdown,
    validate_public_language,
    resolve_binding,
)

__all__ = [
    "AbiCompatibilityPolicy",
    "BindingCapabilities",
    "BindingRoute",
    "BINDINGS_BY_LANGUAGE",
    "COMMAND_EVENT_SCHEMA",
    "EVENT_VALIDATION_FIELDS",
    "OFFICIAL_PUBLIC_LANGUAGES",
    "OFFICIAL_PUBLIC_ROUTE_MATRIX",
    "PUBLIC_RUNTIME_COMMANDS",
    "ABI_POLICY_BY_ROUTE",
    "ROUTE_OPERATIONAL_LIMITS",
    "PYTHON_BINDING",
    "JAVASCRIPT_BINDING",
    "RUST_BINDING",
    "resolve_command_event",
    "route_matrix_markdown",
    "validate_public_language",
    "resolve_binding",
]
