"""Façade interna oficial para compile/transpile/runtime.

Contrato inmutable para capas superiores (CLI/imports/stdlib):
- El único punto de entrada interno aprobado es ``pcobra.cobra.build.backend_pipeline``.
- La invocación debe hacerse solo vía ``resolve_backend_runtime``, ``build`` o ``transpile``.
- Queda prohibido llamar transpiladores/adapters oficiales de forma directa.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from pcobra.cobra.architecture.contracts import (
    PUBLIC_BACKENDS,
    PUBLIC_CAPABILITIES_CONTRACT,
    assert_backend_allowed_for_scope,
    binding_route_for_public_backend,
)
from pcobra.cobra.bindings.runtime_manager import RuntimeManager
from pcobra.cobra.build.orchestrator import BackendResolution, BuildOrchestrator
from pcobra.core.ast_cache import obtener_ast

ORCHESTRATOR = BuildOrchestrator()
RUNTIME_MANAGER = RuntimeManager()
INTERNAL_BACKEND_ENTRYPOINT = "pcobra.cobra.build.backend_pipeline"
INTERNAL_BACKEND_API_CONTRACT: tuple[str, ...] = (
    "resolve_backend_runtime",
    "build",
    "transpile",
)


def _load_official_transpilers() -> dict[str, type]:
    """Helper interno: encapsula acceso al registro canónico."""
    from pcobra.cobra.transpilers.registry import build_official_transpilers

    return build_official_transpilers()


TRANSPILERS: dict[str, type] = _load_official_transpilers()


def _public_route_backend_matrix() -> dict[str, tuple[str, ...]]:
    """Matriz explícita de rutas públicas que usan resolución de backend."""
    contract_backends = tuple(PUBLIC_CAPABILITIES_CONTRACT)
    return {
        "build_pipeline.resolve_backend": contract_backends,
        "build_pipeline.resolve_backend_runtime": contract_backends,
        "build_pipeline.build": contract_backends,
    }


def _validate_public_route_startup_contract() -> None:
    """Falla en arranque si una ruta pública deriva en backend fuera del contrato."""
    for route_name, backends in _public_route_backend_matrix().items():
        for backend in backends:
            assert_backend_allowed_for_scope(backend=backend, scope="public")
            binding_route_for_public_backend(backend)
        out_of_contract = tuple(backend for backend in backends if backend not in PUBLIC_BACKENDS)
        if out_of_contract:
            raise RuntimeError(
                "Ruta pública configurada con backend fuera de python/javascript/rust. "
                f"route={route_name}; invalid={out_of_contract}; public={PUBLIC_BACKENDS}"
            )


_validate_public_route_startup_contract()


def _validate_internal_entrypoint_contract() -> None:
    """Valida que el contrato interno de entrypoint permanezca inmutable."""
    if INTERNAL_BACKEND_ENTRYPOINT != "pcobra.cobra.build.backend_pipeline":
        raise RuntimeError(
            "El entrypoint interno oficial debe ser pcobra.cobra.build.backend_pipeline."
        )
    if INTERNAL_BACKEND_API_CONTRACT != ("resolve_backend_runtime", "build", "transpile"):
        raise RuntimeError(
            "El contrato interno del backend pipeline debe ser "
            "resolve_backend_runtime/build/transpile."
        )


_validate_internal_entrypoint_contract()


def _resolve_backend(source: str, hints: dict[str, Any] | None = None) -> BackendResolution:
    """Resuelve backend canónico internamente a partir de source/hints."""
    context = hints or {}
    preferred_backend = context.get("preferred_backend")
    required_capabilities = tuple(context.get("required_capabilities", ()))
    route_scope = "internal_migration" if context.get("internal_migration", False) else "public"
    return ORCHESTRATOR.resolve_backend(
        source_file=source,
        preferred_backend=preferred_backend,
        required_capabilities=required_capabilities,
        route_scope=route_scope,
    )


def resolve_backend_runtime(
    source: str,
    hints: dict[str, Any] | None = None,
) -> tuple[BackendResolution, dict[str, str]]:
    """Resuelve backend y metadatos de bridge/runtime para el contrato de bindings."""
    context = hints or {}
    resolution = _resolve_backend(source, context)
    if not context.get("internal_migration", False):
        assert_backend_allowed_for_scope(backend=resolution.backend, scope="public")
    capabilities, bridge = RUNTIME_MANAGER.resolve_runtime(resolution.backend)
    abi_version = RUNTIME_MANAGER.validate_abi_route(
        resolution.backend,
        abi_version=context.get("abi_version"),
    )
    runtime_context = {
        "language": capabilities.language,
        "route": capabilities.route.value,
        "bridge": bridge.implementation,
        "security_profile": bridge.security_profile,
        "abi_contract": capabilities.abi_contract,
        "abi_version": abi_version,
    }
    return resolution, runtime_context


def transpile(ast: Any, backend: str) -> str:
    """Transpila un AST al backend indicado usando el registro oficial."""
    if backend not in TRANSPILERS:
        raise ValueError(f"Transpilador no soportado: {backend}")
    transpiler = TRANSPILERS[backend]()
    return transpiler.generate_code(ast)


def build(source: str, hints: dict[str, Any] | None = None) -> dict[str, Any]:
    """Pipeline completo: resolver backend, construir AST y transpilar código.

    Contrato interno de invocación: ``build(source, hints)``.
    """
    context = dict(hints or {})

    source_path = Path(source)
    if source_path.exists() and source_path.is_file():
        source_file = str(source_path)
        codigo = source_path.read_text(encoding="utf-8")
    else:
        source_file = str(context.get("source_file", "<memory>"))
        codigo = source

    resolution, runtime_context = resolve_backend_runtime(source_file, context)
    ast = obtener_ast(codigo)
    code = transpile(ast, resolution.backend)
    debug = bool(context.get("debug", False))
    reason = resolution.reason_for(debug=debug)
    return {
        "backend": resolution.backend,
        "reason": reason,
        "runtime": runtime_context,
        "ast": ast,
        "code": code,
    }


__all__ = [
    "INTERNAL_BACKEND_ENTRYPOINT",
    "INTERNAL_BACKEND_API_CONTRACT",
    "ORCHESTRATOR",
    "TRANSPILERS",
    "build",
    "resolve_backend_runtime",
    "transpile",
]
