"""Registro de progreso estructurado para CobraInstaller."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Callable, Mapping, Sequence

LogLevel = str
ProgressCallback = Callable[["ProgressEvent"], None]
LegacyCallback = Callable[[str], None]


@dataclass(frozen=True, slots=True)
class ProgressEvent:
    """Evento emitido por el flujo de construcción Cobra."""

    level: LogLevel
    message: str
    stage: str | None = None
    step: int | None = None
    total_steps: int | None = None
    metadata: Mapping[str, object] = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def format(self) -> str:
        """Devuelve una representación legible para CLI e interfaces simples."""

        prefix = self.level.upper()
        if (
            self.level == "step"
            and self.step is not None
            and self.total_steps is not None
        ):
            prefix = f"PASO {self.step}/{self.total_steps}"
        elif self.stage:
            prefix = f"{prefix} {self.stage}"
        return f"[{prefix}] {self.message}"

    def __str__(self) -> str:
        return self.format()


class BuildLogger:
    """Logger de build con niveles y callbacks de eventos/progreso."""

    def __init__(
        self,
        *callbacks: ProgressCallback,
        legacy_callback: LegacyCallback | None = None,
    ) -> None:
        self._callbacks: list[ProgressCallback] = list(callbacks)
        self._legacy_callback = legacy_callback
        self.events: list[ProgressEvent] = []

    def add_callback(self, callback: ProgressCallback) -> None:
        """Registra un callback adicional que recibirá ``ProgressEvent``."""

        self._callbacks.append(callback)

    def info(
        self, message: str, *, stage: str | None = None, **metadata: object
    ) -> ProgressEvent:
        return self.emit("info", message, stage=stage, metadata=metadata)

    def warning(
        self, message: str, *, stage: str | None = None, **metadata: object
    ) -> ProgressEvent:
        return self.emit("warning", message, stage=stage, metadata=metadata)

    def error(
        self, message: str, *, stage: str | None = None, **metadata: object
    ) -> ProgressEvent:
        return self.emit("error", message, stage=stage, metadata=metadata)

    def step(
        self,
        message: str,
        *,
        stage: str,
        step: int | None = None,
        total_steps: int | None = None,
        **metadata: object,
    ) -> ProgressEvent:
        return self.emit(
            "step",
            message,
            stage=stage,
            step=step,
            total_steps=total_steps,
            metadata=metadata,
        )

    def emit(
        self,
        level: LogLevel,
        message: str,
        *,
        stage: str | None = None,
        step: int | None = None,
        total_steps: int | None = None,
        metadata: Mapping[str, object] | None = None,
    ) -> ProgressEvent:
        event = ProgressEvent(
            level=level,
            message=message,
            stage=stage,
            step=step,
            total_steps=total_steps,
            metadata=dict(metadata or {}),
        )
        self.events.append(event)
        for callback in tuple(self._callbacks):
            callback(event)
        if self._legacy_callback is not None:
            self._legacy_callback(event.message)
        return event


def emit_many(
    logger: BuildLogger, messages: Sequence[str], *, stage: str | None = None
) -> None:
    """Emite varias líneas informativas preservando el callback legado."""

    for message in messages:
        logger.info(message, stage=stage)


__all__ = ["BuildLogger", "ProgressCallback", "ProgressEvent", "emit_many"]
