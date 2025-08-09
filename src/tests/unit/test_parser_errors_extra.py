import pytest
from cobra.core import Lexer
from cobra.core import Parser, ParserError


def parse(code: str):
    tokens = Lexer(code).analizar_token()
    return Parser(tokens)


def test_decorator_without_function():
    codigo = "@d var x = 1"
    with pytest.raises(ParserError):
        parse(codigo).parsear()


def test_desde_without_import():
    codigo = "desde 'm' x"
    with pytest.raises(ParserError):
        parse(codigo).parsear()


def test_unclosed_macro():
    codigo = "macro m { var x = 1 "
    with pytest.raises(ParserError):
        parse(codigo).parsear()

def test_condicional_sino_sin_fin():
    codigo = """
    si x > 0:
        imprimir(x)
    sino:
        imprimir(x)
    """
    with pytest.raises(ParserError):
        parse(codigo).parsear()


def test_macro_llaves_desbalanceadas():
    codigo = "macro m { var x = 1 }}"
    with pytest.raises(ParserError):
        parse(codigo).parsear()
