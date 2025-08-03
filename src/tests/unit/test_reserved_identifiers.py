import pytest
from cobra.lexico.lexer import Lexer
from cobra.parser.parser import Parser, ParserError


def test_variable_nombre_reservado():
    codigo = "var si = 1"
    tokens = Lexer(codigo).analizar_token()
    parser = Parser(tokens)
    with pytest.raises(ParserError, match="palabra reservada"):
        parser.parsear()


def test_funcion_nombre_reservado():
    codigo = """
    func mientras():
        fin
    """
    tokens = Lexer(codigo).analizar_token()
    parser = Parser(tokens)
    with pytest.raises(ParserError, match="palabra reservada"):
        parser.parsear()


def test_parametro_nombre_reservado():
    codigo = """
    func foo(para):
        fin
    """
    tokens = Lexer(codigo).analizar_token()
    parser = Parser(tokens)
    with pytest.raises(ParserError, match="palabra reservada"):
        parser.parsear()
