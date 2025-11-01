"""Parser alternativo basado en Lark para cargar la gramática EBNF."""
from __future__ import annotations

from dataclasses import fields, is_dataclass
from pathlib import Path
import sys
from types import ModuleType
from typing import Iterable, List, Optional
import json

_LARK_DISPONIBLE = False

try:  # pragma: no cover - ruta directa cuando ``lark`` está instalado.
    from lark import Lark, ParseError, Tree  # type: ignore[import-not-found]
except ImportError:  # pragma: no cover - la rama se prueba con los tests existentes
    class ParseError(Exception):
        """Excepción compatible con :mod:`lark` para la ruta de reserva."""

    class Tree:  # pylint: disable=too-few-public-methods
        """Implementación mínima del nodo ``Tree`` de Lark."""

        def __init__(self, data: str, children: Optional[List["Tree"]] = None) -> None:
            self.data = data
            self.children = list(children or [])

        def __repr__(self) -> str:  # pragma: no cover - utilitario de depuración
            return f"Tree({self.data!r}, {self.children!r})"

    class _LarkPlaceholder:  # pylint: disable=too-few-public-methods
        """Objeto marcador usado únicamente para conservar la API externa."""

        def __init__(self, *args, **kwargs) -> None:  # noqa: D401 - firma fija
            self.args = args
            self.kwargs = kwargs

        def parse(self, _source: str):  # pragma: no cover - no debería invocarse
            raise ParseError(
                "El parser de Lark no está disponible en esta instalación."
            )

    _mod = ModuleType("lark")
    _mod.Lark = _LarkPlaceholder
    _mod.ParseError = ParseError
    _mod.Tree = Tree
    sys.modules.setdefault("lark", _mod)
    Lark = _LarkPlaceholder
else:
    _LARK_DISPONIBLE = True

from pcobra.cobra.core import Token, TipoToken


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
        grammar_path = self._resolver_ruta_gramatica()

        try:
            with open(grammar_path, "r", encoding="utf-8") as f:
                grammar = f.read()
        except FileNotFoundError as exc:
            raise FileNotFoundError(
                "No se encuentra el archivo de gramática"
            ) from exc

        if not grammar.strip():
            raise ValueError("El archivo de gramática está vacío")

        self._grammar = grammar
        self._lark = Lark(grammar, start="start") if _LARK_DISPONIBLE else None

    @staticmethod
    def _resolver_ruta_gramatica() -> Path:
        """Intenta localizar ``gramatica.ebnf`` ascendiendo desde el módulo."""

        candidatos: Iterable[Path] = (
            parent / "docs" / "gramatica.ebnf" for parent in Path(__file__).resolve().parents
        )
        for candidato in candidatos:
            if candidato.is_file():
                return candidato
        # Si no se encuentra en ninguno de los directorios ascendentes, exponer error claro
        raise FileNotFoundError("No se encuentra el archivo de gramática")

    def _tokens_to_source(self) -> str:
        """
        Convierte la lista de tokens a una cadena legible para depuración.

        Esta representación mantiene los comportamientos históricos del
        proyecto, como escapar las cadenas con ``json.dumps`` y utilizar
        ``repr`` para el resto de tokens. Es la que emplean los tests
        unitarios para validar que la conversión conserva caracteres
        especiales.
        """

        parts = []
        for t in self.tokens:
            if t.tipo == TipoToken.EOF:
                continue
            if t.tipo == TipoToken.CADENA:
                parts.append(json.dumps(t.valor))
            else:
                parts.append("None" if t.valor is None else repr(t.valor))
        return " ".join(parts)

    def _tokens_to_code(self) -> str:
        """Reconstruye el código fuente aproximado a partir de los tokens."""

        lexemas = []
        for t in self.tokens:
            if t.tipo == TipoToken.EOF:
                continue
            if t.tipo == TipoToken.CADENA:
                lexemas.append(json.dumps(t.valor))
                continue

            valor = t.valor
            if valor is None:
                lexemas.append("")
            else:
                lexemas.append(str(valor))

        return " ".join(part for part in lexemas if part)

    def parsear(self) -> Optional[object]:
        """
        Realiza el parsing de los tokens.

        Returns:
            Optional[object]: Árbol de parsing resultante o None si hay error

        Raises:
            ParseError: Si ocurre un error durante el parsing
        """
        source = self._tokens_to_code()
        if _LARK_DISPONIBLE:
            try:
                return self._lark.parse(source)
            except ParseError as exc:  # pragma: no cover - dependiente de gramática
                raise ParseError(f"Error durante el parsing: {str(exc)}") from exc

        return self._parse_with_clasic_parser()

    # --- Ruta de compatibilidad cuando Lark no está disponible -----------------

    def _parse_with_clasic_parser(self) -> Optional[Tree]:
        """Genera un árbol sintético utilizando el parser clásico."""

        try:
            from pcobra.cobra.core.parser import ClassicParser
        except ImportError as exc:  # pragma: no cover - protección adicional
            raise ParseError("No es posible cargar el parser clásico de Cobra.") from exc

        classic_parser = ClassicParser(self.tokens)
        try:
            ast = classic_parser.parsear()
        except Exception as exc:  # pragma: no cover - errores específicos del parser
            raise ParseError(f"Error durante el parsing clásico: {exc}") from exc

        return self._ast_to_tree(ast)

    def _ast_to_tree(self, node) -> Optional[Tree]:
        """Convierte nodos AST de Cobra en nodos :class:`Tree` compatibles."""

        mapping = {
            "NodoAsignacion": "asignacion",
            "NodoBucleMientras": "bucle_mientras",
            "NodoSwitch": "switch",
            "NodoCase": "case",
            "NodoPara": "bucle_para",
            "NodoFor": "bucle_para",
        }

        if isinstance(node, list):
            children = [child for child in (self._ast_to_tree(item) for item in node) if child]
            if not children:
                return None
            if len(children) == 1:
                return children[0]
            return Tree("group", children)

        if is_dataclass(node):
            name = node.__class__.__name__
            children: List[Tree] = []

            for field in fields(node):
                value = getattr(node, field.name)
                if isinstance(value, list):
                    children.extend(
                        child
                        for child in (self._ast_to_tree(item) for item in value)
                        if child is not None
                    )
                else:
                    child = self._ast_to_tree(value)
                    if child is not None:
                        children.append(child)

            if name == "NodoFuncion":
                asincrona = getattr(node, "asincronica", False)
                etiqueta = "funcion_asincronica" if asincrona else "funcion"
                return Tree(etiqueta, children)

            if name in mapping:
                return Tree(mapping[name], children)

            if children:
                if len(children) == 1:
                    return children[0]
                return Tree("group", children)

            return None

        return None
