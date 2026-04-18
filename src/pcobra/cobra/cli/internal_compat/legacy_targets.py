"""Gating temporal para targets legacy internos.

Este módulo concentra la ruta de compatibilidad interna controlada para
backends legacy (`go/cpp/java/wasm/asm`) sin exponerlos en la UX pública.
"""

from __future__ import annotations

import os
from datetime import date
from typing import Final

from pcobra.cobra.internal_compat.legacy_contracts import (
    INTERNAL_BACKENDS,
    INTERNAL_COMPATIBILITY_RETIREMENT_WINDOW,
)

LEGACY_BACKENDS_FEATURE_FLAG: Final[str] = "COBRA_INTERNAL_LEGACY_TARGETS"


def is_internal_legacy_targets_enabled() -> bool:
    """Indica si la compatibilidad temporal de targets internos está habilitada."""
    raw = (os.environ.get(LEGACY_BACKENDS_FEATURE_FLAG, "") or "").strip().lower()
    return raw in {"1", "true", "yes", "on"}


def enabled_internal_legacy_targets() -> tuple[str, ...]:
    """Devuelve el set legacy disponible cuando la flag temporal está activa."""
    if not is_internal_legacy_targets_enabled():
        return ()
    return tuple(
        target
        for target in INTERNAL_BACKENDS
        if not is_internal_legacy_target_retired(target)
    )


def _retirement_window_end(window: str) -> date:
    """Convierte ventana `Qn YYYY` a fecha de corte (fin de trimestre)."""
    quarter, year = window.split()
    quarter_to_month_day = {
        "Q1": (3, 31),
        "Q2": (6, 30),
        "Q3": (9, 30),
        "Q4": (12, 31),
    }
    month, day = quarter_to_month_day[quarter.strip().upper()]
    return date(int(year), month, day)


def is_internal_legacy_target_retired(target: str, *, today: date | None = None) -> bool:
    """Indica si un backend legacy superó su ventana de retiro contractual."""
    if target not in INTERNAL_COMPATIBILITY_RETIREMENT_WINDOW:
        return False
    reference = today or date.today()
    end = _retirement_window_end(INTERNAL_COMPATIBILITY_RETIREMENT_WINDOW[target])
    return reference > end
