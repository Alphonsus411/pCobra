import pytest
from cobra.lexico.lexer import Lexer
from cobra.parser.parser import Parser


def parse(code: str):
    tokens = Lexer(code).analizar_token()
    return Parser(tokens)


def test_decorator_without_function():
    codigo = "@d var x = 1"
    with pytest.raises(SyntaxError):
        parse(codigo).parsear()


def test_desde_without_import():
    codigo = "desde 'm' x"
    with pytest.raises(SyntaxError):
        parse(codigo).parsear()


def test_unclosed_macro():
    codigo = "macro m { var x = 1 "
    with pytest.raises(SyntaxError):
        parse(codigo).parsear()

def test_condicional_sino_sin_fin():
    codigo = """
    si x > 0:
        imprimir(x)
    sino:
        imprimir(x)
    """
    with pytest.raises(SyntaxError):
        parse(codigo).parsear()


def test_macro_llaves_desbalanceadas():
    codigo = "macro m { var x = 1 }}"
    with pytest.raises(SyntaxError):
        parse(codigo).parsear()
