"""Namespace interno de compatibilidad legacy para transpiladores no oficiales."""

from __future__ import annotations

import os

_LEGACY_TRANSPILERS_OPT_IN_ENV = "PCOBRA_ENABLE_LEGACY_TRANSPILERS"


def assert_legacy_transpilers_enabled() -> None:
    """Exige opt-in explícito para cargar transpiladores legacy internos."""
    if os.environ.get(_LEGACY_TRANSPILERS_OPT_IN_ENV) == "1":
        return
    raise RuntimeError(
        "CONTRACT_ERROR: los transpiladores legacy internos están deshabilitados por defecto. "
        f"Defina {_LEGACY_TRANSPILERS_OPT_IN_ENV}=1 solo para flujos internos de compatibilidad."
    )


__all__ = ["assert_legacy_transpilers_enabled"]
