"""Shim legacy de ``bindings`` dentro de ``src``.

Este módulo solo delega en :mod:`pcobra.cobra.bindings`.
"""

from .contract import (
    BINDINGS_BY_LANGUAGE,
    BindingCapabilities,
    BindingRoute,
    JAVASCRIPT_BINDING,
    PYTHON_BINDING,
    RUST_BINDING,
    resolve_binding,
)

__all__ = [
    "BindingCapabilities",
    "BindingRoute",
    "BINDINGS_BY_LANGUAGE",
    "PYTHON_BINDING",
    "JAVASCRIPT_BINDING",
    "RUST_BINDING",
    "resolve_binding",
]
