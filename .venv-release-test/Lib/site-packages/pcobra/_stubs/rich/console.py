"""Implementación mínima de ``rich.console`` utilizada en las pruebas."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

RenderableType = Any


class Group:
    """Agrupa renderizables manteniendo la firma de Rich."""

    def __init__(self, *renderables: Any) -> None:
        self.renderables = list(renderables)

    def __iter__(self):  # pragma: no cover - compatibilidad
        return iter(self.renderables)


class _ConsoleGroup:
    def __init__(self, console: "Console", title: str | None) -> None:
        self._console = console
        self._title = title

    def __enter__(self) -> "Console":  # pragma: no cover - comportamiento trivial
        if self._title is not None:
            self._console.print(self._title)
        return self._console

    def __exit__(self, *exc_info: object) -> None:  # pragma: no cover - comportamiento trivial
        return None


class Console:
    """Consola simple que captura mensajes en memoria."""

    def __init__(self, *, record: bool = False) -> None:
        self._record = record
        self._log: list[str] = []

    def print(self, *objetos: Any, style: str | None = None, **_: Any) -> None:
        texto = " ".join(str(objeto) for objeto in objetos)
        if self._record:
            self._log.append(texto)

    def export_text(self) -> str:
        return "\n".join(self._log)

    def clear(self) -> None:  # pragma: no cover - comportamiento trivial
        self._log.clear()

    def status(self, mensaje: str, *, spinner: str = "dots") -> "Status":
        from .status import Status

        return Status(self, mensaje, spinner=spinner)

    def group(self, titulo: str | None = None) -> _ConsoleGroup:
        return _ConsoleGroup(self, titulo)


__all__ = ["Console", "Group", "RenderableType"]
