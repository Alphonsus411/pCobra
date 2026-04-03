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


def test_condicional_si_valido_con_dos_puntos_espaciado():
    codigo = """
si 1 == 1 :
    imprimir "ok"
fin
"""
    ast = parse(codigo).parsear()
    assert ast, "Se esperaba AST no vacío para condicional válido"


def test_condicional_si_sin_dos_puntos_lanza_parser_error():
    codigo = """
si 1 == 1
    imprimir "ok"
fin
"""
    with pytest.raises(ParserError) as exc_info:
        parse(codigo).parsear()

    assert str(exc_info.value) == "Se esperaba ':' después de la condición del 'si'"


def test_condicional_si_sin_fin_lanza_parser_error():
    codigo = """
si 1 == 1 :
    imprimir "ok"
"""
    with pytest.raises(ParserError) as exc_info:
        parse(codigo).parsear()

    assert str(exc_info.value) == "Se esperaba 'fin' para cerrar el bloque condicional"


def test_macro_llaves_desbalanceadas():
    codigo = "macro m { var x = 1 }}"
    with pytest.raises(ParserError):
        parse(codigo).parsear()
