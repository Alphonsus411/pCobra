"""Shim legacy de ``bindings`` dentro de ``src``.

Alcance explícito de compatibilidad:
- **Permitido únicamente** para consumidores legacy externos al código
  productivo de ``src/pcobra/**``.
- Código nuevo debe usar imports canónicos ``pcobra.cobra.bindings.*``.
- Este módulo existe sólo como puente temporal y está deprecado.

Implementación: delega en :mod:`pcobra.cobra.bindings`.
"""
# pcobra-compat: allow-legacy-imports

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
