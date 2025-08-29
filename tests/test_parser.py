import sys
from pathlib import Path

import pytest

sys.path.append(str(Path(__file__).resolve().parent.parent / "pCobra"))
from cobra.core.lexer import Lexer
from cobra.core.parser import ClassicParser, ParserError
from core.ast_nodes import NodoAsignacion



def test_parser_asignacion_simple() -> None:
    codigo = "var x = 5"
    tokens = Lexer(codigo).tokenizar()
    parser = ClassicParser(tokens)
    ast = parser.parsear()
    nodo = ast[0]
    assert isinstance(nodo, NodoAsignacion)
    assert nodo.identificador == "x"
    assert nodo.valor.valor == 5


def test_parser_error_sintaxis() -> None:
    codigo = "mientras 1"
    tokens = Lexer(codigo).tokenizar()
    parser = ClassicParser(tokens)
    with pytest.raises(ParserError):
        parser.parsear()
    assert parser.errores
