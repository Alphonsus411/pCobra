"""Façade interna para resolución de backend y transpilación."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from pcobra.cobra.bindings.runtime_manager import RuntimeManager
from pcobra.cobra.build.orchestrator import BackendResolution, BuildOrchestrator
from pcobra.cobra.transpilers.registry import build_official_transpilers
from pcobra.core.ast_cache import obtener_ast

ORCHESTRATOR = BuildOrchestrator()
RUNTIME_MANAGER = RuntimeManager()
TRANSPILERS: dict[str, type] = build_official_transpilers()


def resolve_backend(source: str, hints: dict[str, Any] | None = None) -> BackendResolution:
    """Resuelve backend canónico a partir de un source file y pistas opcionales."""
    context = hints or {}
    preferred_backend = context.get("preferred_backend")
    required_capabilities = tuple(context.get("required_capabilities", ()))
    return ORCHESTRATOR.resolve_backend(
        source_file=source,
        preferred_backend=preferred_backend,
        required_capabilities=required_capabilities,
    )


def resolve_backend_runtime(
    source: str,
    hints: dict[str, Any] | None = None,
) -> tuple[BackendResolution, dict[str, str]]:
    """Resuelve backend y metadatos de bridge/runtime para el contrato de bindings."""
    context = hints or {}
    resolution = resolve_backend(source, context)
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
    reason = (
        resolution.reason_for(debug=debug)
        if hasattr(resolution, "reason_for")
        else (getattr(resolution, "reason", None) if debug else None)
    )
    return {
        "backend": resolution.backend,
        "reason": reason,
        "runtime": runtime_context,
        "ast": ast,
        "code": code,
    }


__all__ = [
    "ORCHESTRATOR",
    "TRANSPILERS",
    "build",
    "resolve_backend",
    "resolve_backend_runtime",
    "transpile",
]
