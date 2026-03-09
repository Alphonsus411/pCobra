"""Mínimo viable de ``rich.progress`` para las pruebas unitarias."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Iterable

TaskID = int


class SpinnerColumn:  # pragma: no cover - comportamiento trivial
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        pass


class BarColumn:  # pragma: no cover - comportamiento trivial
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self.bar_width = kwargs.get('bar_width')


class TextColumn:
    def __init__(self, template: str) -> None:  # pragma: no cover - trivial
        self.template = template


class TimeElapsedColumn:  # pragma: no cover - comportamiento trivial
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        pass


class TimeRemainingColumn:  # pragma: no cover - comportamiento trivial
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        pass


@dataclass
class _Task:
    descripcion: str
    total: float | None
    completed: float = 0.0


class Progress:
    def __init__(self, *columnas: Any, console: Any | None = None, transient: bool = True) -> None:
        self.columns = columnas
        self.console = console
        self.transient = transient
        self._tasks: Dict[TaskID, _Task] = {}
        self._contador = 0

    def add_task(self, descripcion: str, *, total: float | None = None) -> TaskID:
        self._contador += 1
        self._tasks[self._contador] = _Task(descripcion=descripcion, total=total, completed=0.0)
        return self._contador

    def update(self, task_id: TaskID, *, advance: float | None = None, completed: float | None = None) -> None:
        tarea = self._tasks[task_id]
        if advance is not None:
            tarea.completed += advance
        if completed is not None:
            tarea.completed = completed

    def advance(self, task_id: TaskID, amount: float = 1.0) -> None:  # pragma: no cover - trivial
        self.update(task_id, advance=amount)

    def __enter__(self) -> "Progress":  # pragma: no cover - trivial
        return self

    def __exit__(self, *exc_info: object) -> None:  # pragma: no cover - trivial
        return None

    @property
    def tasks(self) -> list[_Task]:
        return [self._tasks[task_id] for task_id in sorted(self._tasks)]


__all__ = [
    "Progress",
    "TaskID",
    "SpinnerColumn",
    "BarColumn",
    "TextColumn",
    "TimeElapsedColumn",
    "TimeRemainingColumn",
]
