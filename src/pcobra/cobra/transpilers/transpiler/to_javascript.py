"""Alias canónico del transpiler JavaScript oficial.

Mantiene compatibilidad interna hacia ``to_js`` sin exponer rutas legacy.
"""

from pcobra.cobra.transpilers.transpiler.to_js import TranspiladorJavaScript

__all__ = ["TranspiladorJavaScript"]
