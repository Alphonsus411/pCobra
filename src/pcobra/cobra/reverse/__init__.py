"""Cadena de transpilación inversa extendida para la distribución pcobra."""
from __future__ import annotations

from typing import List, Any

import pcobra.cobra.transpilers.reverse as _legacy_reverse
from pcobra.cobra.transpilers.reverse import BaseReverseTranspiler

from .hololang_parser import HololangParser, parse_hololang

__all__ = list(getattr(_legacy_reverse, "__all__", []))

globals().update({name: getattr(_legacy_reverse, name) for name in __all__})


class ReverseFromHololang(BaseReverseTranspiler):
    """Transpilador inverso básico desde Hololang hacia nodos AST de Cobra."""

    LANGUAGE = "hololang"

    def generate_ast(self, code: str) -> List[Any]:
        parser = HololangParser()
        return parser.parse(code)


__all__.extend(["HololangParser", "parse_hololang", "ReverseFromHololang"])
