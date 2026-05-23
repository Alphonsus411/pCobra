"""Stub del componente ``Panel``."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class Panel:
    renderable: Any
    title: str | None = None
    border_style: str | None = None
    style: str | None = None

    def __init__(self, renderable: Any, *, title: str | None = None, border_style: str | None = None, style: str | None = None, expand: bool | None = None, **_: Any) -> None:
        self.renderable = renderable
        self.title = title
        self.border_style = border_style
        self.style = style
        self.expand = expand


__all__ = ["Panel"]
