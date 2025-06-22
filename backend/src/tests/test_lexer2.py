from src.cobra.lexico.lexer import Lexer, TipoToken


def test_lexer_asignacion_variable():
    codigo = 'var x = holobit([0.8, -0.5, 1.2])'
    lexer = Lexer(codigo)
    tokens = lexer.analizar_token()
    assert [(token.tipo, token.valor) for token in tokens] == [
        (TipoToken.VAR, 'var'),
        (TipoToken.IDENTIFICADOR, 'x'),
        (TipoToken.ASIGNAR, '='),
        (TipoToken.HOLOBIT, 'holobit'),
        (TipoToken.LPAREN, '('),
        (TipoToken.LBRACKET, '['),  # Corchete de apertura
        (TipoToken.FLOTANTE, 0.8),
        (TipoToken.COMA, ','),  # Coma entre elementos
        (TipoToken.RESTA, '-'),
        (TipoToken.FLOTANTE, 0.5),
        (TipoToken.COMA, ','),
        (TipoToken.FLOTANTE, 1.2),
        (TipoToken.RBRACKET, ']'),  # Corchete de cierre
        (TipoToken.RPAREN, ')'),
        (TipoToken.EOF, None)
    ]
