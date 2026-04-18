"""Compat shim: resolución mínima de backend redirigida a backend_pipeline.

Este módulo existe solo para compatibilidad técnica temporal.
La API interna aprobada para resolver/transpilar está en
``pcobra.cobra.build.backend_pipeline``.

Fecha objetivo de retiro del shim: 2026-09-30.
"""

from __future__ import annotations

from typing import Any, Mapping

from pcobra.cobra.build import backend_pipeline
from pcobra.cobra.backends.base import BackendAdapter

SHIM_RETIREMENT_TARGET = "2026-09-30"

_BACKEND_ALIASES = {
    "python": "python",
    "py": "python",
    "javascript": "javascript",
    "js": "javascript",
    "rust": "rust",
    "rs": "rust",
}


class PipelineBackendAdapter(BackendAdapter):
    """Adapter mínimo que delega en la fachada interna del pipeline."""

    def __init__(self, backend: str) -> None:
        self.backend = backend

    def compile(self, ast: Any, options: Mapping[str, Any] | None = None) -> str:
        return backend_pipeline.transpile(ast, self.backend)


def resolve_backend(artifact_kind: str) -> BackendAdapter:
    """Retorna un adapter shim que delega en ``backend_pipeline.transpile``."""
    normalized = _BACKEND_ALIASES.get((artifact_kind or "").strip().lower())
    if normalized in {"python", "javascript", "rust"}:
        return PipelineBackendAdapter(normalized)
    raise ValueError(f"artifact_kind no soportado: {artifact_kind!r}")


def compile(
    ast: Any,
    artifact_kind: str,
    options: Mapping[str, Any] | None = None,
) -> str:
    """API de compatibilidad que redirige explícitamente al pipeline.

    Args:
        ast: AST de Cobra (o estructura normalizable por el transpiler).
        artifact_kind: Tipo de artefacto de salida (python/javascript/rust).
        options: Opciones internas del backend (reservado para evolución futura).
    """
    del options  # Reservado para mantener firma compat.
    normalized = _BACKEND_ALIASES.get((artifact_kind or "").strip().lower())
    if normalized is None:
        raise ValueError(f"artifact_kind no soportado: {artifact_kind!r}")
    return backend_pipeline.transpile(ast, normalized)
