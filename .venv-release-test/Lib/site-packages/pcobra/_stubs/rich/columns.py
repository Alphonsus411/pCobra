"""Stub de :mod:`rich.columns` utilizado en las pruebas."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable


@dataclass
class Columns:
    renderables: list[Any]
    title: str | None = None
    equal: bool = True
    padding: int | None = None

    def __init__(self, renderables: Iterable[Any], *, title: str | None = None, equal: bool = True, padding: int | None = None, expand: bool | None = None, **_: Any) -> None:
        self.renderables = list(renderables)
        self.title = title
        self.equal = equal
        self.padding = padding
        self.expand = expand


__all__ = ["Columns"]
