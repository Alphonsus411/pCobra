import pytest
from src.core.lexer import Lexer
from src.core.parser import Parser


def test_variable_nombre_reservado():
    codigo = "var si = 1"
    tokens = Lexer(codigo).analizar_token()
    parser = Parser(tokens)
    with pytest.raises(SyntaxError, match="palabra reservada"):
        parser.parsear()


def test_funcion_nombre_reservado():
    codigo = """
    func mientras():
        fin
    """
    tokens = Lexer(codigo).analizar_token()
    parser = Parser(tokens)
    with pytest.raises(SyntaxError, match="palabra reservada"):
        parser.parsear()
