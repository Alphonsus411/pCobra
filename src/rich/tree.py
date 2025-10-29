"""Versión reducida de ``rich.tree``."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, List


@dataclass
class Tree:
    label: str
    children: List["Tree"] = field(default_factory=list)

    def add(self, label: str) -> "Tree":
        nodo = Tree(label)
        self.children.append(nodo)
        return nodo


__all__ = ["Tree"]
