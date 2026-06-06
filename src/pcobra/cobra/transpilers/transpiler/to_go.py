"""Shim de compatibilidad para el transpilador Go legacy."""

from __future__ import annotations

import os

_FLAG = "PCOBRA_ENABLE_LEGACY_TRANSPILERS"
_previous = os.environ.get(_FLAG)
os.environ[_FLAG] = "1"
try:
    from pcobra.cobra.transpilers.transpiler.legacy.to_go import *  # noqa: F403
finally:
    if _previous is None:
        os.environ.pop(_FLAG, None)
    else:
        os.environ[_FLAG] = _previous
