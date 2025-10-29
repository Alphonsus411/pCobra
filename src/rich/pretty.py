"""Stub sencillo de ``rich.pretty``."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class Pretty:
    objeto: Any

    def __str__(self) -> str:  # pragma: no cover - representación auxiliar
        return repr(self.objeto)


__all__ = ["Pretty"]
