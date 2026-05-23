"""Reexporta el analizador semántico desde el nuevo espacio de nombres."""

from pcobra.cobra.semantico import *  # noqa: F401,F403

__all__ = list(globals().get("__all__", []))
