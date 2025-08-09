import pytest
from cobra.core import Lexer
from cobra.core import Parser, ParserError


def parse_code(code: str) -> Parser:
    tokens = Lexer(code).analizar_token()
    return Parser(tokens)


def test_para_sin_dospuntos():
    codigo = "para i in range(0,5) imprimir(i)"
    with pytest.raises(ParserError):
        parse_code(codigo).parsear()


def test_mientras_parentesis_sin_cerrar():
    codigo = "mientras (x < 3"
    with pytest.raises(ParserError):
        parse_code(codigo).parsear()


def test_intentar_sin_capturar():
    codigo = "intentar: lanzar 1 fin"
    with pytest.raises(ParserError):
        parse_code(codigo).parsear()
