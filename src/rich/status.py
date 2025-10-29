"""Context manager simplificado para ``Console.status``."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class Status:
    console: Any
    mensaje: str
    spinner: str = "dots"

    def __enter__(self) -> "Status":  # pragma: no cover - trivial
        return self

    def __exit__(self, *exc_info: object) -> None:  # pragma: no cover - trivial
        return None


__all__ = ["Status"]
