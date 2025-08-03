import pytest
from cobra.lexico.lexer import Lexer
from cobra.parser.parser import Parser, ParserError


def parsear_codigo(codigo: str):
    tokens = Lexer(codigo).analizar_token()
    return Parser(tokens)


def test_asignacion_sin_identificador():
    codigo = "var = 5"
    with pytest.raises(ParserError):
        parsear_codigo(codigo).parsear()


def test_condicional_sin_dospuntos():
    codigo = "si x > 0 imprimir(x) fin"
    with pytest.raises(ParserError):
        parsear_codigo(codigo).parsear()
