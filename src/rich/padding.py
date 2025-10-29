"""Stub del helper :mod:`rich.padding`."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Tuple


@dataclass
class Padding:
    renderable: Any
    pad: Tuple[int, int, int, int]


__all__ = ["Padding"]
