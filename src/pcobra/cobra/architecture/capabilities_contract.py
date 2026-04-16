"""Contrato único de capacidades públicas para resolución de backend.

Este contrato centraliza:
1) backends públicos permitidos,
2) ruta de binding por backend público,
3) política de fallback para rutas públicas.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Final

from pcobra.cobra.architecture.backend_policy import INTERNAL_BACKENDS, PUBLIC_BACKENDS
from pcobra.cobra.bindings.contract import BindingRoute


@dataclass(frozen=True, slots=True)
class PublicBackendCapability:
    """Capacidad pública canónica para un backend soportado."""

    backend: str
    binding_route: BindingRoute
    fallback_rank: int


PUBLIC_CAPABILITIES_CONTRACT: Final[dict[str, PublicBackendCapability]] = {
    "python": PublicBackendCapability(
        backend="python",
        binding_route=BindingRoute.PYTHON_DIRECT_IMPORT,
        fallback_rank=1,
    ),
    "javascript": PublicBackendCapability(
        backend="javascript",
        binding_route=BindingRoute.JAVASCRIPT_RUNTIME_BRIDGE,
        fallback_rank=2,
    ),
    "rust": PublicBackendCapability(
        backend="rust",
        binding_route=BindingRoute.RUST_COMPILED_FFI,
        fallback_rank=3,
    ),
}

# Política de fallback contractual para rutas públicas.
PUBLIC_FALLBACK_POLICY: Final[tuple[str, ...]] = tuple(
    backend
    for backend, _metadata in sorted(
        PUBLIC_CAPABILITIES_CONTRACT.items(),
        key=lambda item: item[1].fallback_rank,
    )
)

# Preferencias públicas por tipo de proyecto (siempre restringidas al contrato público).
PROJECT_TYPE_PUBLIC_POLICY: Final[dict[str, tuple[str, ...]]] = {
    "library": ("python", "rust", "javascript"),
    "web": ("javascript", "python", "rust"),
    "systems": ("rust", "python", "javascript"),
    "embedded": ("rust", "python", "javascript"),
    "application": ("python", "javascript", "rust"),
}


def validate_capabilities_contract() -> None:
    """Valida consistencia interna del contrato público."""

    configured_public = tuple(PUBLIC_CAPABILITIES_CONTRACT)
    if configured_public != PUBLIC_BACKENDS:
        raise RuntimeError(
            "PUBLIC_CAPABILITIES_CONTRACT debe listar exactamente PUBLIC_BACKENDS. "
            f"configured={configured_public}; expected={PUBLIC_BACKENDS}"
        )

    missing = tuple(backend for backend in PUBLIC_BACKENDS if backend not in PUBLIC_FALLBACK_POLICY)
    extras = tuple(backend for backend in PUBLIC_FALLBACK_POLICY if backend not in PUBLIC_BACKENDS)
    if missing or extras:
        raise RuntimeError(
            "PUBLIC_FALLBACK_POLICY debe cubrir exactamente PUBLIC_BACKENDS. "
            f"missing={missing or '∅'}; extras={extras or '∅'}"
        )

    for project_type, candidates in PROJECT_TYPE_PUBLIC_POLICY.items():
        invalid = tuple(backend for backend in candidates if backend not in PUBLIC_BACKENDS)
        if invalid:
            raise RuntimeError(
                "PROJECT_TYPE_PUBLIC_POLICY contiene backends fuera del contrato público. "
                f"project_type={project_type}; invalid={invalid}"
            )


def assert_backend_allowed_for_scope(*, backend: str, scope: str) -> None:
    """Garantiza que un backend pertenezca al scope autorizado."""

    canonical = (backend or "").strip().lower()
    if scope == "public":
        if canonical not in PUBLIC_BACKENDS:
            raise ValueError(
                f"Backend no permitido en ruta pública: {backend}. "
                f"Permitidos: {', '.join(PUBLIC_BACKENDS)}"
            )
        return
    if scope == "internal_migration":
        if canonical not in PUBLIC_BACKENDS and canonical not in INTERNAL_BACKENDS:
            raise ValueError(
                f"Backend no reconocido para migración interna: {backend}. "
                f"Permitidos: {', '.join(PUBLIC_BACKENDS + INTERNAL_BACKENDS)}"
            )
        return
    raise ValueError(f"Scope de backend no soportado: {scope}")


def binding_route_for_public_backend(backend: str) -> BindingRoute:
    """Devuelve la ruta de binding contractual de un backend público."""

    assert_backend_allowed_for_scope(backend=backend, scope="public")
    return PUBLIC_CAPABILITIES_CONTRACT[backend].binding_route


validate_capabilities_contract()


__all__ = [
    "PROJECT_TYPE_PUBLIC_POLICY",
    "PUBLIC_CAPABILITIES_CONTRACT",
    "PUBLIC_FALLBACK_POLICY",
    "PublicBackendCapability",
    "assert_backend_allowed_for_scope",
    "binding_route_for_public_backend",
    "validate_capabilities_contract",
]
