"""Adapter interno para compilación a Python."""

from __future__ import annotations

from typing import Any, Mapping

from pcobra.cobra.backends.base import BackendAdapter
from pcobra.cobra.transpilers.transpiler.to_python import TranspiladorPython


class PythonAdapter(BackendAdapter):
    """Wrapper sobre ``TranspiladorPython`` sin modificar su implementación."""

    def compile(self, ast: Any, options: Mapping[str, Any] | None = None) -> str:
        _ = options or {}
        transpiler = TranspiladorPython()
        return transpiler.generate_code(ast)
