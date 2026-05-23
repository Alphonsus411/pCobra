"""Stub de :mod:`rich.markdown` para las pruebas."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class Markdown:
    text: str
    kwargs: dict[str, Any]

    def __init__(self, text: str, **kwargs: Any) -> None:
        self.text = text
        self.kwargs = kwargs


__all__ = ["Markdown"]
