"""Adapter interno para compilación a Rust."""

from __future__ import annotations

from typing import Any, Mapping

from pcobra.cobra.backends.base import BackendAdapter
from pcobra.cobra.transpilers.transpiler.to_rust import TranspiladorRust


class RustAdapter(BackendAdapter):
    """Wrapper sobre ``TranspiladorRust`` sin modificar su implementación."""

    def compile(self, ast: Any, options: Mapping[str, Any] | None = None) -> str:
        _ = options or {}
        transpiler = TranspiladorRust()
        return transpiler.generate_code(ast)
