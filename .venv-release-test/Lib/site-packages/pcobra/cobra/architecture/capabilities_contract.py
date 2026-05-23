"""Compatibilidad de contrato: re-exporta el canon desde ``architecture.contracts``."""

from pcobra.cobra.architecture.contracts import (
    PROJECT_TYPE_PUBLIC_POLICY,
    PUBLIC_BACKENDS,
    PUBLIC_CAPABILITIES_CONTRACT,
    PUBLIC_FALLBACK_POLICY,
    PublicBackendCapability,
    assert_backend_allowed_for_scope,
    binding_route_for_public_backend,
    validate_capabilities_contract,
)

__all__ = [
    "PROJECT_TYPE_PUBLIC_POLICY",
    "PUBLIC_BACKENDS",
    "PUBLIC_CAPABILITIES_CONTRACT",
    "PUBLIC_FALLBACK_POLICY",
    "PublicBackendCapability",
    "assert_backend_allowed_for_scope",
    "binding_route_for_public_backend",
    "validate_capabilities_contract",
]
