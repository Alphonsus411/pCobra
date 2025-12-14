"""Reexporta el analizador léxico desde el nuevo espacio de nombres ``pcobra.core``.

Este módulo actúa como envoltorio ligero sobre ``pcobra.cobra.core.lexer``
para mantener compatibilidad con el código existente sin duplicar lógica.
"""

from pcobra.cobra.core.lexer import *  # noqa: F401,F403

__all__ = list(globals().get("__all__", []))
