"""Reexporta traducciones CLI desde el nuevo espacio de nombres."""

from pcobra.cobra.cli.i18n import *  # noqa: F401,F403

__all__ = list(globals().get("__all__", []))
