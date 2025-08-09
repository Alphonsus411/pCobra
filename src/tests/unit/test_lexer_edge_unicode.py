import pytest
from cobra.lexico.lexer import Lexer, TipoToken


def test_identificadores_unicode():
    codigo = "var á = 1\nvar βeta = 2"
    tokens = Lexer(codigo).analizar_token()
    assert [(t.tipo, t.valor) for t in tokens] == [
        (TipoToken.VAR, 'var'),
        (TipoToken.IDENTIFICADOR, 'á'),
        (TipoToken.ASIGNAR, '='),
        (TipoToken.ENTERO, 1),
        (TipoToken.VAR, 'var'),
        (TipoToken.IDENTIFICADOR, 'βeta'),
        (TipoToken.ASIGNAR, '='),
        (TipoToken.ENTERO, 2),
        (TipoToken.EOF, None),
    ]


def test_cadenas_escape_mixtas():
    codigo = 'var texto = "Linea1\\r\\nLinea2\\tTab"'
    tokens = Lexer(codigo).analizar_token()
    assert [(t.tipo, t.valor) for t in tokens] == [
        (TipoToken.VAR, 'var'),
        (TipoToken.IDENTIFICADOR, 'texto'),
        (TipoToken.ASIGNAR, '='),
        (TipoToken.CADENA, "Linea1\r\nLinea2\tTab"),
        (TipoToken.EOF, None),
    ]


def test_comentarios_anidados_y_linea_en_bloque():
    codigo = """
    var x = 1 /* comentario externo
                 /* comentario interno */
                 // comentario de linea dentro
               */ var y = 2
    """
    tokens = Lexer(codigo).analizar_token()
    assert [(t.tipo, t.valor) for t in tokens] == [
        (TipoToken.VAR, 'var'),
        (TipoToken.IDENTIFICADOR, 'x'),
        (TipoToken.ASIGNAR, '='),
        (TipoToken.ENTERO, 1),
        (TipoToken.VAR, 'var'),
        (TipoToken.IDENTIFICADOR, 'y'),
        (TipoToken.ASIGNAR, '='),
        (TipoToken.ENTERO, 2),
        (TipoToken.EOF, None),
    ]
