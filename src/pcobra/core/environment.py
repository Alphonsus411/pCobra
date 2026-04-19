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

    def set(self, name: str, value: Any) -> Any:
        """Actualiza ``name`` en su scope más cercano; si no existe, lo define local."""
        if name in self.values:
            self.values[name] = value
            return value
        if self.parent is not None:
            return self.parent.set(name, value)
        self.values[name] = value
        return value
