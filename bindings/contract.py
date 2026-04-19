"""Fachada legacy del contrato de bindings.

Fuente canónica: ``pcobra.cobra.bindings._contract_impl``.
"""

from pcobra.cobra.bindings._contract_impl import (
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
    RouteOperationalLimits,
    resolve_binding,
    resolve_command_event,
    route_matrix_markdown,
    validate_public_language,
)

__all__ = [
    "AbiCompatibilityPolicy",
    "BindingCapabilities",
    "BindingRoute",
    "BINDINGS_BY_LANGUAGE",
    "OFFICIAL_PUBLIC_LANGUAGES",
    "PUBLIC_RUNTIME_COMMANDS",
    "OFFICIAL_PUBLIC_ROUTE_MATRIX",
    "ABI_POLICY_BY_ROUTE",
    "COMMAND_EVENT_SCHEMA",
    "EVENT_VALIDATION_FIELDS",
    "ROUTE_OPERATIONAL_LIMITS",
    "RouteOperationalLimits",
    "JAVASCRIPT_BINDING",
    "PYTHON_BINDING",
    "RUST_BINDING",
    "route_matrix_markdown",
    "resolve_command_event",
    "validate_public_language",
    "resolve_binding",
]
