"""Entorno léxico para resolución y asignación de variables en runtime."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class Environment:
    """Representa un contexto de variables enlazado a un entorno padre."""

    values: dict[str, Any] = field(default_factory=dict)
    parent: Environment | None = None

    def get(self, name: str) -> Any:
        """Obtiene ``name`` desde el entorno actual o alguno de sus ancestros."""
        if name in self.values:
            return self.values[name]
        if self.parent is not None:
            return self.parent.get(name)
        raise NameError(f"Variable no declarada: {name}")

    def define(self, name: str, value: Any) -> Any:
        """Define siempre ``name`` en el entorno local."""
        self.values[name] = value
        return value

    def contains(self, name: str) -> bool:
        """Indica si ``name`` existe en este entorno o en alguno ancestro."""
        if name in self.values:
            return True
        if self.parent is not None:
            return self.parent.contains(name)
        return False

    def set(self, name: str, value: Any) -> Any:
        """Actualiza ``name`` en su scope más cercano o falla si no existe."""
        if name in self.values:
            self.values[name] = value
            return value
        if self.parent is not None and self.parent.contains(name):
            return self.parent.set(name, value)
        raise NameError(f"Variable no declarada: {name}")

    def delete(self, name: str) -> None:
        """Elimina ``name`` en el primer scope donde exista."""
        if name in self.values:
            del self.values[name]
            return
        if self.parent is not None:
            self.parent.delete(name)
            return
        raise NameError(f"Variable no declarada: {name}")
