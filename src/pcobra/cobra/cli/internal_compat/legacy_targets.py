"""Gating temporal para targets legacy internos.

Este módulo concentra la ruta de compatibilidad interna controlada para
backends legacy (`go/cpp/java/wasm/asm`) sin exponerlos en la UX pública.
"""

from __future__ import annotations

import os
from typing import Final

from pcobra.cobra.architecture.backend_policy import INTERNAL_BACKENDS

LEGACY_BACKENDS_FEATURE_FLAG: Final[str] = "COBRA_INTERNAL_LEGACY_TARGETS"


def is_internal_legacy_targets_enabled() -> bool:
    """Indica si la compatibilidad temporal de targets internos está habilitada."""
    raw = (os.environ.get(LEGACY_BACKENDS_FEATURE_FLAG, "") or "").strip().lower()
    return raw in {"1", "true", "yes", "on"}


def enabled_internal_legacy_targets() -> tuple[str, ...]:
    """Devuelve el set legacy disponible cuando la flag temporal está activa."""
    if not is_internal_legacy_targets_enabled():
        return ()
    return INTERNAL_BACKENDS

