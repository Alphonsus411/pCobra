"""Interfaces base para adapters de compilación interna."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Mapping


class BackendAdapter(ABC):
    """Contrato mínimo que deben implementar los adapters de backend."""

    @abstractmethod
    def compile(self, ast: Any, options: Mapping[str, Any] | None = None) -> str:
        """Compila un AST de Cobra y retorna el artefacto generado."""
        raise NotImplementedError
