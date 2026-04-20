"""Shim legacy para el contrato de bindings.

Fuente de verdad: :mod:`pcobra.cobra.bindings.contract`.
"""

from __future__ import annotations

import warnings

from pcobra.cobra.bindings.contract import (
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

warnings.warn(
    "`bindings.contract` está deprecado; usa `pcobra.cobra.bindings.contract`.",
    DeprecationWarning,
    stacklevel=2,
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
    "RouteOperationalLimits",
    "PYTHON_BINDING",
    "JAVASCRIPT_BINDING",
    "RUST_BINDING",
    "resolve_command_event",
    "route_matrix_markdown",
    "validate_public_language",
    "resolve_binding",
]
