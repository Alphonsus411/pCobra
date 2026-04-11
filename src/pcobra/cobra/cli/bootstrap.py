"""Bootstrap utilities for CLI startup concerns."""

from __future__ import annotations

import os
import sys


def reconfigurar_consola_utf8() -> None:
    """Fuerza UTF-8 en stdout/stderr cuando el runtime lo soporta."""
    for stream_name in ("stdout", "stderr"):
        stream = getattr(sys, stream_name, None)
        reconfigure = getattr(stream, "reconfigure", None)
        if not callable(reconfigure):
            continue
        try:
            reconfigure(encoding="utf-8")
        except Exception:
            # Fail-safe: no bloquear el arranque del CLI por la consola.
            pass

    try:
        if os.name == "nt":
            os.system("chcp 65001 > nul")
    except Exception:
        # Fail-safe: no bloquear el arranque del CLI por ajustes del OS.
        pass

    os.environ.setdefault("PYTHONIOENCODING", "utf-8")
