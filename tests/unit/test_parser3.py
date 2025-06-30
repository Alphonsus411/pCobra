import pytest
from src.cobra.parser.parser import Parser
from src.core.ast_nodes import NodoAsignacion, NodoHolobit, NodoCondicional, NodoBucleMientras, NodoFuncion, NodoLlamadaFuncion, NodoValor
from src.cobra.lexico.lexer import TipoToken, Token


def generar_tokens(*args):
    """
    Helper para crear una secuencia de tokens en el formato [(tipo, valor), ...].
    """
    return [Token(tipo, valor) for tipo, valor in args]


def test_asignacion_variable():
    tokens = generar_tokens(
        (TipoToken.VAR, "var"),
        (TipoToken.IDENTIFICADOR, "x"),
        (TipoToken.ASIGNAR, "="),
        (TipoToken.ENTERO, 10),
        (TipoToken.EOF, None)
    )
    parser = Parser(tokens)
    ast = parser.parsear()
    assert len(ast) == 1
    assert isinstance(ast[0], NodoAsignacion)
    assert ast[0].variable.valor == "x"
    assert isinstance(ast[0].expresion, NodoValor)
    assert ast[0].expresion.valor == 10


def test_asignacion_holobit():
    tokens = generar_tokens(
        (TipoToken.VAR, "var"),
        (TipoToken.IDENTIFICADOR, "h"),
        (TipoToken.ASIGNAR, "="),
        (TipoToken.HOLOBIT, "holobit"),
        (TipoToken.LPAREN, "("),
        (TipoToken.LBRACKET, "["),
        (TipoToken.ENTERO, 1),
        (TipoToken.COMA, ","),
        (TipoToken.ENTERO, 2),
        (TipoToken.RBRACKET, "]"),
        (TipoToken.RPAREN, ")"),
        (TipoToken.EOF, None)
    )
    parser = Parser(tokens)
    ast = parser.parsear()
    assert len(ast) == 1
    assert isinstance(ast[0], NodoAsignacion)
    assert isinstance(ast[0].expresion, NodoHolobit)
    assert [val.valor for val in ast[0].expresion.valores] == [1, 2]


def test_condicional():
    tokens = generar_tokens(
        (TipoToken.SI, "si"),
        (TipoToken.ENTERO, 1),
        (TipoToken.MAYORQUE, ">"),
        (TipoToken.ENTERO, 0),
        (TipoToken.DOSPUNTOS, ":"),
        (TipoToken.IDENTIFICADOR, "hacer_algo"),
        (TipoToken.LPAREN, "("),
        (TipoToken.RPAREN, ")"),
        (TipoToken.FIN, "fin"),
        (TipoToken.EOF, None)
    )
    parser = Parser(tokens)
    ast = parser.parsear()
    assert len(ast) == 1
    assert isinstance(ast[0], NodoCondicional)
    assert ast[0].condicion.izquierda.valor == 1
    assert ast[0].condicion.derecha.valor == 0
    assert len(ast[0].bloque_si) == 1
    assert isinstance(ast[0].bloque_si[0], NodoLlamadaFuncion)


def test_bucle_mientras():
    tokens = generar_tokens(
        (TipoToken.MIENTRAS, "mientras"),
        (TipoToken.IDENTIFICADOR, "x"),
        (TipoToken.MAYORQUE, ">"),
        (TipoToken.ENTERO, 0),
        (TipoToken.DOSPUNTOS, ":"),
        (TipoToken.IDENTIFICADOR, "hacer_algo"),
        (TipoToken.LPAREN, "("),
        (TipoToken.RPAREN, ")"),
        (TipoToken.FIN, "fin"),
        (TipoToken.EOF, None)
    )
    parser = Parser(tokens)
    ast = parser.parsear()
    assert len(ast) == 1
    assert isinstance(ast[0], NodoBucleMientras)
    assert ast[0].condicion.izquierda.valor == "x"
    assert ast[0].condicion.derecha.valor == 0
    assert len(ast[0].cuerpo) == 1
    assert isinstance(ast[0].cuerpo[0], NodoLlamadaFuncion)


def test_funcion():
    tokens = generar_tokens(
        (TipoToken.FUNC, "func"),
        (TipoToken.IDENTIFICADOR, "mi_funcion"),
        (TipoToken.LPAREN, "("),
        (TipoToken.IDENTIFICADOR, "param1"),
        (TipoToken.COMA, ","),
        (TipoToken.IDENTIFICADOR, "param2"),
        (TipoToken.RPAREN, ")"),
        (TipoToken.DOSPUNTOS, ":"),
        (TipoToken.IDENTIFICADOR, "hacer_algo"),
        (TipoToken.LPAREN, "("),
        (TipoToken.RPAREN, ")"),
        (TipoToken.FIN, "fin"),
        (TipoToken.EOF, None)
    )
    parser = Parser(tokens)
    ast = parser.parsear()
    assert len(ast) == 1
    assert isinstance(ast[0], NodoFuncion)
    assert ast[0].nombre == "mi_funcion"
    assert ast[0].parametros == ["param1", "param2"]
    assert len(ast[0].cuerpo) == 1
    assert isinstance(ast[0].cuerpo[0], NodoLlamadaFuncion)


def test_llamada_funcion():
    tokens = generar_tokens(
        (TipoToken.IDENTIFICADOR, "mi_funcion"),
        (TipoToken.LPAREN, "("),
        (TipoToken.ENTERO, 5),
        (TipoToken.COMA, ","),
        (TipoToken.ENTERO, 10),
        (TipoToken.RPAREN, ")"),
        (TipoToken.EOF, None)
    )
    parser = Parser(tokens)
    ast = parser.parsear()
    assert len(ast) == 1
    assert isinstance(ast[0], NodoLlamadaFuncion)
    assert ast[0].nombre == "mi_funcion"
    assert [arg.valor for arg in ast[0].argumentos] == [5, 10]
