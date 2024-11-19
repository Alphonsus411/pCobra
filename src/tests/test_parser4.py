import pytest
from src.core.parser import Parser, NodoAsignacion, NodoBucleMientras, NodoCondicional, NodoFuncion
from src.core.lexer import TipoToken, Token


def test_parser_asignacion():
    tokens = [
        Token(TipoToken.VAR, "var"),
        Token(TipoToken.IDENTIFICADOR, "x"),
        Token(TipoToken.ASIGNAR, "="),
        Token(TipoToken.ENTERO, 5),
        Token(TipoToken.EOF, None),
    ]
    parser = Parser(tokens)
    ast = parser.parsear()

    assert len(ast) == 1
    assert isinstance(ast[0], NodoAsignacion)
    assert ast[0].variable.valor == "x"
    assert ast[0].expresion.valor == 5


def test_parser_mientras():
    tokens = [
        Token(TipoToken.MIENTRAS, "mientras"),
        Token(TipoToken.IDENTIFICADOR, "x"),
        Token(TipoToken.MAYORQUE, ">"),
        Token(TipoToken.ENTERO, 0),
        Token(TipoToken.DOSPUNTOS, ":"),
        Token(TipoToken.IDENTIFICADOR, "x"),
        Token(TipoToken.ASIGNAR, "="),
        Token(TipoToken.IDENTIFICADOR, "x"),
        Token(TipoToken.RESTA, "-"),
        Token(TipoToken.ENTERO, 1),
        Token(TipoToken.FIN, "fin"),
        Token(TipoToken.EOF, None),
    ]
    parser = Parser(tokens)
    ast = parser.parsear()

    assert len(ast) == 1
    assert isinstance(ast[0], NodoBucleMientras)
    assert ast[0].condicion.operador.valor == ">"
    assert len(ast[0].cuerpo) == 1
    assert isinstance(ast[0].cuerpo[0], NodoAsignacion)


def test_parser_condicional():
    tokens = [
        Token(TipoToken.SI, "si"),
        Token(TipoToken.IDENTIFICADOR, "x"),
        Token(TipoToken.MAYORQUE, ">"),
        Token(TipoToken.ENTERO, 10),
        Token(TipoToken.DOSPUNTOS, ":"),
        Token(TipoToken.VAR, "var"),
        Token(TipoToken.IDENTIFICADOR, "y"),
        Token(TipoToken.ASIGNAR, "="),
        Token(TipoToken.ENTERO, 20),
        Token(TipoToken.SINO, "sino"),
        Token(TipoToken.DOSPUNTOS, ":"),
        Token(TipoToken.VAR, "z"),
        Token(TipoToken.ASIGNAR, "="),
        Token(TipoToken.ENTERO, 30),
        Token(TipoToken.FIN, "fin"),
        Token(TipoToken.EOF, None),
    ]
    parser = Parser(tokens)
    ast = parser.parsear()

    assert len(ast) == 1
    assert isinstance(ast[0], NodoCondicional)
    assert ast[0].condicion.operador.valor == ">"
    assert len(ast[0].bloque_si) == 1
    assert len(ast[0].bloque_sino) == 1


def test_parser_funcion():
    tokens = [
        Token(TipoToken.FUNC, "func"),
        Token(TipoToken.IDENTIFICADOR, "miFuncion"),
        Token(TipoToken.LPAREN, "("),
        Token(TipoToken.IDENTIFICADOR, "a"),
        Token(TipoToken.COMA, ","),
        Token(TipoToken.IDENTIFICADOR, "b"),
        Token(TipoToken.RPAREN, ")"),
        Token(TipoToken.DOSPUNTOS, ":"),
        Token(TipoToken.RETORNO, "retorno"),
        Token(TipoToken.IDENTIFICADOR, "a"),
        Token(TipoToken.SUMA, "+"),
        Token(TipoToken.IDENTIFICADOR, "b"),
        Token(TipoToken.FIN, "fin"),
        Token(TipoToken.EOF, None),
    ]
    parser = Parser(tokens)
    ast = parser.parsear()

    assert len(ast) == 1
    assert isinstance(ast[0], NodoFuncion)
    assert ast[0].nombre == "miFuncion"
    assert len(ast[0].parametros) == 2
    assert ast[0].parametros == ["a", "b"]
    assert len(ast[0].cuerpo) == 1


def test_parser_errores():
    tokens = [
        Token(TipoToken.MIENTRAS, "mientras"),
        Token(TipoToken.IDENTIFICADOR, "x"),
        Token(TipoToken.FIN, "fin"),
        Token(TipoToken.EOF, None),
    ]
    parser = Parser(tokens)

    with pytest.raises(SyntaxError):
        parser.parsear()
