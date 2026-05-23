"""Implementación reducida de ``rich.json``."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any
import json as _json


@dataclass
class JSON:
    data: Any
    indent: int | None = None
    sort_keys: bool = True

    def __init__(self, contenido: str, *, indent: int | None = None) -> None:
        self.data = contenido
        self.indent = indent

    @classmethod
    def from_data(
        cls,
        datos: Any,
        *,
        indent: int | None = None,
        sort_keys: bool = True,
    ) -> "JSON":
        instancia = cls(_json.dumps(datos, ensure_ascii=False, indent=indent, sort_keys=sort_keys))
        instancia.sort_keys = sort_keys
        instancia.indent = indent
        return instancia


__all__ = ["JSON"]
