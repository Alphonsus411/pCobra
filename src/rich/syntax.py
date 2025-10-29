"""Stub de :mod:`rich.syntax` con la API mínima usada en las pruebas."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class _Lexer:
    name: str


@dataclass
class Syntax:
    code: str
    lexer: _Lexer

    def __init__(self, code: str, lenguaje: str) -> None:
        self.code = code
        self.lexer = _Lexer(lenguaje)


__all__ = ["Syntax"]
