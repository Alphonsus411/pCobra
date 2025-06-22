import pytest
from src.cobra.lexico.lexer import Lexer, TipoToken, LexerError


def test_lexer_asignacion_variable():
    codigo = 'var x = holobit([0.8, -0.5, 1.2])'
    lexer = Lexer(codigo)
    tokens = lexer.analizar_token()

    assert [(t.tipo, t.valor) for t in tokens] == [
        (TipoToken.VAR, 'var'),
        (TipoToken.IDENTIFICADOR, 'x'),
        (TipoToken.ASIGNAR, '='),
        (TipoToken.HOLOBIT, 'holobit'),
        (TipoToken.LPAREN, '('),
        (TipoToken.LBRACKET, '['),
        (TipoToken.FLOTANTE, 0.8),
        (TipoToken.COMA, ','),
        (TipoToken.RESTA, '-'),
        (TipoToken.FLOTANTE, 0.5),
        (TipoToken.COMA, ','),
        (TipoToken.FLOTANTE, 1.2),
        (TipoToken.RBRACKET, ']'),
        (TipoToken.RPAREN, ')'),
        (TipoToken.EOF, None),
    ]

    assert tokens[0].linea == 1 and tokens[0].columna == 1
    assert tokens[2].columna == 7


def test_lexer_transformacion_holobit():
    codigo = 'transformar(holobit([1.0, 2.0, -0.5]), "rotar", 45)'

    lexer = Lexer(codigo)
    tokens = lexer.analizar_token()

    assert [(t.tipo, t.valor) for t in tokens] == [
        (TipoToken.TRANSFORMAR, 'transformar'),
        (TipoToken.LPAREN, '('),
        (TipoToken.HOLOBIT, 'holobit'),
        (TipoToken.LPAREN, '('),
        (TipoToken.LBRACKET, '['),
        (TipoToken.FLOTANTE, 1.0),
        (TipoToken.COMA, ','),
        (TipoToken.FLOTANTE, 2.0),
        (TipoToken.COMA, ','),
        (TipoToken.RESTA, '-'),
        (TipoToken.FLOTANTE, 0.5),
        (TipoToken.RBRACKET, ']'),
        (TipoToken.RPAREN, ')'),
        (TipoToken.COMA, ','),
        (TipoToken.CADENA, 'rotar'),
        (TipoToken.COMA, ','),
        (TipoToken.ENTERO, 45),
        (TipoToken.RPAREN, ')'),
        (TipoToken.EOF, None),
    ]


def test_lexer_con_comentarios():
    codigo = """
    # Comentario inicial
    var x = 10 // asignar valor
    imprimir(x) /* comentario de bloque */
    """

    lexer = Lexer(codigo)
    tokens = lexer.analizar_token()

    assert [(t.tipo, t.valor) for t in tokens] == [
        (TipoToken.VAR, 'var'),
        (TipoToken.IDENTIFICADOR, 'x'),
        (TipoToken.ASIGNAR, '='),
        (TipoToken.ENTERO, 10),
        (TipoToken.IMPRIMIR, 'imprimir'),
        (TipoToken.LPAREN, '('),
        (TipoToken.IDENTIFICADOR, 'x'),
        (TipoToken.RPAREN, ')'),
        (TipoToken.EOF, None),
    ]


def test_lexer_error_posicion():
    codigo = "var x = $"
    lexer = Lexer(codigo)
    with pytest.raises(LexerError) as exc:
        lexer.tokenizar()
    err = exc.value
    assert err.linea == 1
    assert err.columna == 9

