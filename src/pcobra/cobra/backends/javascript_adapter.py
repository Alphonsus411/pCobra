"""Adapter interno para compilación a JavaScript."""

from __future__ import annotations

from typing import Any, Mapping

from pcobra.cobra.backends.base import BackendAdapter
from pcobra.cobra.transpilers.transpiler.to_js import TranspiladorJavaScript


class JavaScriptAdapter(BackendAdapter):
    """Wrapper sobre ``TranspiladorJavaScript`` sin modificar su implementación."""

    def compile(self, ast: Any, options: Mapping[str, Any] | None = None) -> str:
        _ = options or {}
        transpiler = TranspiladorJavaScript()
        return transpiler.generate_code(ast)
