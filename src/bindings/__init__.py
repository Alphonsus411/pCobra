"""Shim legacy de ``bindings`` dentro de ``src``.

Este módulo delega en :mod:`pcobra.cobra.bindings` y está deprecado.
"""

from __future__ import annotations

import warnings

from .contract import (
    BINDINGS_BY_LANGUAGE,
    BindingCapabilities,
    BindingRoute,
    JAVASCRIPT_BINDING,
    PYTHON_BINDING,
    RUST_BINDING,
    resolve_binding,
)

warnings.warn(
    "`bindings` está deprecado; usa `pcobra.cobra.bindings`.",
    DeprecationWarning,
    stacklevel=2,
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
