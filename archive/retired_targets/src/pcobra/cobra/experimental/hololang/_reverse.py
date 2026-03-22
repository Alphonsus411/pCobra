"""Transpilación inversa experimental desde Hololang.

Este módulo es interno y no forma parte del scope público soportado por
``pcobra.cobra.transpilers.reverse.policy``.
"""
from __future__ import annotations

from typing import Any, List

from pcobra.cobra.transpilers.reverse.base import BaseReverseTranspiler

from ._parser import HololangParser


class ReverseFromHololang(BaseReverseTranspiler):
    """Transpilador inverso experimental desde Hololang."""

    LANGUAGE = "hololang"

    def generate_ast(self, code: str) -> List[Any]:
        return HololangParser().parse(code)
