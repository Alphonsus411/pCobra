"""Compatibilidad pública para reverse transpilation.

Este paquete reexporta únicamente la API pública soportada por
``pcobra.cobra.transpilers.reverse``. Componentes experimentales o legados no
deben exponerse desde aquí.
"""
from __future__ import annotations

import pcobra.cobra.transpilers.reverse as _legacy_reverse

__all__ = list(getattr(_legacy_reverse, "__all__", []))

globals().update({name: getattr(_legacy_reverse, name) for name in __all__})
