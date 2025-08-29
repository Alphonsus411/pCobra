"""Parser alternativo basado en Lark para cargar la gramática EBNF."""
from __future__ import annotations
from pathlib import Path
from typing import List, Optional
import json
try:
    from lark import Lark, ParseError
except ImportError as exc:  # pragma: no cover - dependencia externa
    raise ImportError(
        "No se pudo importar 'lark'. Instálalo ejecutando 'pip install lark-parser'."
    ) from exc
from cobra.core import Token, TipoToken


class LarkParser:
    """Parser basado en Lark que carga la gramática EBNF."""

    def __init__(self, tokens: List[Token]) -> None:
        """
        Inicializa el parser con una lista de tokens.

        Args:
            tokens: Lista de tokens a parsear

        Raises:
            FileNotFoundError: Si no se encuentra el archivo de gramática
            ValueError: Si la gramática está vacía o es inválida
        """
        self.tokens = tokens
        grammar_path = Path(__file__).resolve().parents[3] / "docs" / "gramatica.ebnf"

        try:
            with open(grammar_path, "r", encoding="utf-8") as f:
                grammar = f.read()
        except FileNotFoundError as exc:
            raise FileNotFoundError(
                f"No se encuentra el archivo de gramática: {grammar_path}"
            ) from exc

        if not grammar.strip():
            raise ValueError("El archivo de gramática está vacío")

        self._lark = Lark(grammar, start="start")

    def _tokens_to_source(self) -> str:
        """
        Convierte la lista de tokens a una cadena de texto.

        Returns:
            str: Cadena de texto representando los tokens
        """
        parts = []
        for t in self.tokens:
            if t.tipo == TipoToken.CADENA:
                parts.append(json.dumps(t.valor))
            elif t.tipo == TipoToken.EOF:
                continue
            else:
                parts.append(str(t.valor))
        return " ".join(parts)

    def parsear(self) -> Optional[object]:
        """
        Realiza el parsing de los tokens.

        Returns:
            Optional[object]: Árbol de parsing resultante o None si hay error

        Raises:
            ParseError: Si ocurre un error durante el parsing
        """
        try:
            source = self._tokens_to_source()
            return self._lark.parse(source)
        except ParseError as e:
            raise ParseError(f"Error durante el parsing: {str(e)}")
