"""Simulación simple de los prompts de Rich."""

from __future__ import annotations

from typing import Any, Sequence


class Prompt:
    @classmethod
    def ask(
        cls,
        mensaje: str,
        *,
        console: Any | None = None,
        default: Any | None = None,
        choices: Sequence[str] | None = None,
        show_choices: bool = True,
        show_default: bool = True,
        password: bool = False,
        **_: Any,
    ) -> Any:
        if default is not None:
            return default
        if choices:
            return choices[0]
        return ""


class Confirm:
    @classmethod
    def ask(
        cls,
        mensaje: str,
        *,
        default: bool | None = None,
        console: Any | None = None,
    ) -> bool:
        return bool(default)


class IntPrompt:
    @classmethod
    def ask(
        cls,
        mensaje: str,
        *,
        default: int | None = None,
        console: Any | None = None,
        show_default: bool = True,
        **_: Any,
    ) -> int:
        return int(default or 0)


__all__ = ["Prompt", "Confirm", "IntPrompt"]
