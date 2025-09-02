import pytest
from cobra.core import Token, TipoToken
from cobra.core import Parser, ParserError


def test_error_en_declaracion_para():
    tokens = [
        Token(TipoToken.PARA, "para"),
        Token(TipoToken.IDENTIFICADOR, "i"),
        Token(TipoToken.IN, "in"),
        Token(TipoToken.IDENTIFICADOR, "nums"),
        Token(TipoToken.FIN, "fin"),
        Token(TipoToken.EOF, None),
    ]
    parser = Parser(tokens)
    with pytest.raises(ParserError) as excinfo:
        parser.parsear()
    mensaje = str(excinfo.value)
    assert "Se esperaba ':' después del iterable en 'para'" in mensaje
    assert "Se esperaba 'fin' para cerrar el bucle 'para'" in mensaje


def test_error_en_declaracion_condicional():
    tokens = [
        Token(TipoToken.SI, "si"),
        Token(TipoToken.IDENTIFICADOR, "x"),
        Token(TipoToken.MAYORQUE, ">"),
        Token(TipoToken.ENTERO, 0),
        Token(TipoToken.VAR, "var"),
        Token(TipoToken.IDENTIFICADOR, "y"),
        Token(TipoToken.ASIGNAR, "="),
        Token(TipoToken.ENTERO, 1),
        Token(TipoToken.FIN, "fin"),
        Token(TipoToken.EOF, None),
    ]
    parser = Parser(tokens)
    with pytest.raises(ParserError) as excinfo:
        parser.parsear()
    mensaje = str(excinfo.value)
    assert "Se esperaba ':' después de la condición del 'si'" in mensaje
    assert "Se esperaba 'fin'" not in mensaje


def test_error_en_declaracion_mientras():
    tokens = [
        Token(TipoToken.MIENTRAS, "mientras"),
        Token(TipoToken.IDENTIFICADOR, "x"),
        Token(TipoToken.MAYORQUE, ">"),
        Token(TipoToken.ENTERO, 0),
        Token(TipoToken.DOSPUNTOS, ":"),
        Token(TipoToken.EOF, None),
    ]
    parser = Parser(tokens)
    with pytest.raises(ParserError) as excinfo:
        parser.parsear()
    mensaje = str(excinfo.value)
    assert "Se esperaba 'fin' para cerrar el bucle 'mientras'" in mensaje
