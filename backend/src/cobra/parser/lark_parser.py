from __future__ import annotations

from pathlib import Path
from typing import List

from lark import Lark
from src.cobra.lexico.lexer import Token, TipoToken


class LarkParser:
    """Parser basado en Lark que carga la gramática EBNF."""

    def __init__(self, tokens: List[Token]):
        grammar_path = Path(__file__).resolve().parents[3] / "docs" / "gramatica.ebnf"
        with open(grammar_path, "r", encoding="utf-8") as f:
            grammar = f.read()
        self._lark = Lark(grammar, start="start")
        self.tokens = tokens

    def _tokens_to_source(self) -> str:
        parts = []
        for t in self.tokens:
            if t.tipo == TipoToken.CADENA:
                parts.append(f'"{t.valor}"')
            elif t.tipo == TipoToken.EOF:
                continue
            else:
                parts.append(str(t.valor))
        return " ".join(parts)

    def parsear(self):
        source = self._tokens_to_source()
        return self._lark.parse(source)
