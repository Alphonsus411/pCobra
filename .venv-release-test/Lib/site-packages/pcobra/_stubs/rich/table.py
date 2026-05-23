"""Implementación simplificada de ``rich.table``."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, List


@dataclass
class _Column:
    header: str
    style: str | None = None
    _cells: List[str] = field(default_factory=list)


class Table:
    def __init__(self, *, title: str | None = None, header_style: str | None = None) -> None:
        self.title = title
        self.header_style = header_style
        self.columns: list[_Column] = []

    def add_column(self, header: str, *, style: str | None = None) -> None:
        self.columns.append(_Column(header=header, style=style))

    def add_row(self, *valores: Any) -> None:
        if not self.columns:
            for indice, _ in enumerate(valores):
                self.add_column(f"columna_{indice + 1}")
        for columna, valor in zip(self.columns, valores):
            columna._cells.append(str(valor))
        if len(valores) < len(self.columns):
            for columna in self.columns[len(valores):]:
                columna._cells.append("")


__all__ = ["Table"]
