"""Resolución y API interna única de compilación por backend."""

from __future__ import annotations

from typing import Any, Mapping

from pcobra.cobra.backends.base import BackendAdapter
from pcobra.cobra.backends.javascript_adapter import JavaScriptAdapter
from pcobra.cobra.backends.python_adapter import PythonAdapter
from pcobra.cobra.backends.rust_adapter import RustAdapter

_BACKEND_ALIASES = {
    "python": "python",
    "py": "python",
    "javascript": "javascript",
    "js": "javascript",
    "rust": "rust",
    "rs": "rust",
}


def resolve_backend(artifact_kind: str) -> BackendAdapter:
    """Retorna el adapter adecuado para el ``artifact_kind`` solicitado."""
    normalized = _BACKEND_ALIASES.get((artifact_kind or "").strip().lower())
    if normalized == "python":
        return PythonAdapter()
    if normalized == "javascript":
        return JavaScriptAdapter()
    if normalized == "rust":
        return RustAdapter()
    raise ValueError(f"artifact_kind no soportado: {artifact_kind!r}")


def compile(
    ast: Any,
    artifact_kind: str,
    options: Mapping[str, Any] | None = None,
) -> str:
    """API interna unificada de compilación.

    Args:
        ast: AST de Cobra (o estructura normalizable por el transpiler).
        artifact_kind: Tipo de artefacto de salida (python/javascript/rust).
        options: Opciones internas del backend (reservado para evolución futura).
    """
    adapter = resolve_backend(artifact_kind)
    return adapter.compile(ast, options=options)
