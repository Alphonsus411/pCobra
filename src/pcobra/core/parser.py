"""Reexporta el analizador sintáctico bajo ``pcobra.core`` sin modificar su lógica."""

from pcobra.cobra.core.parser import *  # noqa: F401,F403

__all__ = list(globals().get("__all__", []))
