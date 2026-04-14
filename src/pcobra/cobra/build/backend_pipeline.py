"""Façade interna para resolución de backend y transpilación."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from pcobra.cobra.build.orchestrator import BackendResolution, BuildOrchestrator
from pcobra.cobra.transpilers.registry import build_official_transpilers
from pcobra.core.ast_cache import obtener_ast

ORCHESTRATOR = BuildOrchestrator()
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


def transpile(ast: Any, backend: str) -> str:
    """Transpila un AST al backend indicado usando el registro oficial."""
    if backend not in TRANSPILERS:
        raise ValueError(f"Transpilador no soportado: {backend}")
    transpiler = TRANSPILERS[backend]()
    return transpiler.generate_code(ast)


def build(source: str, mode: dict[str, Any] | str | None = None) -> dict[str, Any]:
    """Pipeline completo: resolver backend, construir AST y transpilar código."""
    hints: dict[str, Any]
    if isinstance(mode, dict):
        hints = dict(mode)
    else:
        hints = {"preferred_backend": mode} if mode else {}

    source_path = Path(source)
    if source_path.exists() and source_path.is_file():
        source_file = str(source_path)
        codigo = source_path.read_text(encoding="utf-8")
    else:
        source_file = str(hints.get("source_file", "<memory>"))
        codigo = source

    resolution = resolve_backend(source_file, hints)
    ast = obtener_ast(codigo)
    code = transpile(ast, resolution.backend)
    return {
        "backend": resolution.backend,
        "reason": resolution.reason,
        "ast": ast,
        "code": code,
    }


__all__ = [
    "ORCHESTRATOR",
    "TRANSPILERS",
    "build",
    "resolve_backend",
    "transpile",
]
