import pytest
from io import StringIO
from unittest.mock import patch

from src.core.lexer import Token, TipoToken
from src.core.parser import Parser
from src.core.ast_nodes import NodoTryCatch, NodoThrow, NodoImprimir, NodoIdentificador, NodoValor
from src.core.transpiler.to_js import TranspiladorJavaScript


def generar_tokens(*args):
    return [Token(t, v) for t, v in args]


def test_parser_try_catch_throw():
    tokens = generar_tokens(
        (TipoToken.TRY, "try"),
        (TipoToken.DOSPUNTOS, ":"),
        (TipoToken.THROW, "throw"),
        (TipoToken.CADENA, "error"),
        (TipoToken.CATCH, "catch"),
        (TipoToken.IDENTIFICADOR, "e"),
        (TipoToken.DOSPUNTOS, ":"),
        (TipoToken.IMPRIMIR, "imprimir"),
        (TipoToken.LPAREN, "("),
        (TipoToken.IDENTIFICADOR, "e"),
        (TipoToken.RPAREN, ")"),
        (TipoToken.FIN, "fin"),
        (TipoToken.EOF, None),
    )
    parser = Parser(tokens)
    ast = parser.parsear()
    assert len(ast) == 1
    nodo = ast[0]
    assert isinstance(nodo, NodoTryCatch)
    assert isinstance(nodo.bloque_try[0], NodoThrow)
    assert isinstance(nodo.bloque_catch[0], NodoImprimir)


def test_interpreter_try_catch():
    nodo = NodoTryCatch(
        [NodoThrow(NodoIdentificador("mensaje"))],
        "e",
        [NodoImprimir(NodoIdentificador("e"))],
    )
    interp = InterpretadorCobra()
    interp.variables["mensaje"] = "hola"
    interp.ejecutar_nodo(nodo)
    assert interp.variables["e"] == "hola"


def test_transpiler_python_try_catch():
    nodo = NodoTryCatch(
        [NodoThrow(NodoValor("1"))],
        "e",
        [NodoImprimir(NodoIdentificador("e"))],
    )
    tr = TranspiladorPython()
    codigo = tr.transpilar([nodo])
    esperado = "try:\n    raise Exception(1)\nexcept Exception as e:\n    print(e)\n"
    assert codigo == esperado


def test_transpiler_js_try_catch():
    nodo = NodoTryCatch(
        [NodoThrow(NodoValor("1"))],
        "e",
        [NodoImprimir(NodoIdentificador("e"))],
    )
    tr = TranspiladorJavaScript()
    codigo = tr.transpilar([nodo])
    esperado = "try {\nthrow 1;\n}\ncatch (e) {\nconsole.log(e);\n}"
    assert codigo == esperado
