import sys
from pathlib import Path

import pytest

sys.path.append(str(Path(__file__).resolve().parent.parent / "src"))
from pcobra.cobra.core.lexer import Lexer
from pcobra.cobra.core.parser import ClassicParser, ParserError
from pcobra.core.ast_nodes import (
    NodoAsignacion,
    NodoGarantia,
    NodoOperacionBinaria,
    NodoRetorno,
    NodoValor,
)
from pcobra.core.lexer import TipoToken



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


def test_parser_garantia_con_escape_terminador() -> None:
    codigo = """
garantia x > 0:
    imprimir(x)
sino:
    retorno x
fin
"""
    tokens = Lexer(codigo).tokenizar()
    parser = ClassicParser(tokens)
    ast = parser.parsear()
    nodo = ast[0]
    assert isinstance(nodo, NodoGarantia)
    assert len(nodo.bloque_continuacion) == 1
    assert isinstance(nodo.bloque_escape[-1], NodoRetorno)
    assert not parser.advertencias


def test_parser_garantia_emite_advertencia_si_no_termina() -> None:
    codigo = """
garantia listo:
    pasar
sino:
    imprimir(listo)
fin
"""
    tokens = Lexer(codigo).tokenizar()
    parser = ClassicParser(tokens)
    parser.parsear()
    assert parser.advertencias


def test_parser_igualdad_y_desigualdad_construyen_operacion_binaria() -> None:
    codigo = """
var eq = "hola" == "hola"
var ne = "hola" != "mundo"
"""
    tokens = Lexer(codigo).tokenizar()
    parser = ClassicParser(tokens)
    ast = parser.parsear()

    nodo_eq = ast[0].valor
    nodo_ne = ast[1].valor

    assert isinstance(nodo_eq, NodoOperacionBinaria)
    assert nodo_eq.operador.tipo == TipoToken.IGUAL
    assert isinstance(nodo_eq.izquierda, NodoValor)
    assert isinstance(nodo_eq.derecha, NodoValor)

    assert isinstance(nodo_ne, NodoOperacionBinaria)
    assert nodo_ne.operador.tipo == TipoToken.DIFERENTE
    assert isinstance(nodo_ne.izquierda, NodoValor)
    assert isinstance(nodo_ne.derecha, NodoValor)


def test_parser_suma_con_cadenas_construye_operacion_binaria() -> None:
    codigo = 'var saludo = "hola" + " mundo"'
    tokens = Lexer(codigo).tokenizar()
    parser = ClassicParser(tokens)
    ast = parser.parsear()

    expr = ast[0].valor

    assert isinstance(expr, NodoOperacionBinaria)
    assert expr.operador.tipo == TipoToken.SUMA
    assert isinstance(expr.izquierda, NodoValor)
    assert expr.izquierda.valor == "hola"
    assert isinstance(expr.derecha, NodoValor)
    assert expr.derecha.valor == " mundo"
