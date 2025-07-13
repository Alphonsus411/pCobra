from cobra.lexico.lexer import Lexer, TipoToken


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


def test_keyword_clase_recognized():
    codigo = "clase Persona:"
    lexer = Lexer(codigo)
    tokens = lexer.analizar_token()

    assert [(t.tipo, t.valor) for t in tokens] == [
        (TipoToken.CLASE, "clase"),
        (TipoToken.IDENTIFICADOR, "Persona"),
        (TipoToken.DOSPUNTOS, ":"),
        (TipoToken.EOF, None),
    ]


def test_lexer_func_and_definir_tokens():
    """Verifica que 'func' y 'definir' generan el mismo token FUNC"""
    codigo = "func definir"
    tokens = Lexer(codigo).analizar_token()

    assert [(t.tipo, t.valor) for t in tokens] == [
        (TipoToken.FUNC, "func"),
        (TipoToken.FUNC, "definir"),
        (TipoToken.EOF, None),
    ]


def test_lexer_comentarios_ignorados():
    codigo = """
    # inicio
    func prueba() // comentario al final de linea
    /* bloque
       de comentario */
    """
    tokens = Lexer(codigo).analizar_token()

    assert [(t.tipo, t.valor) for t in tokens] == [
        (TipoToken.FUNC, "func"),
        (TipoToken.IDENTIFICADOR, "prueba"),
        (TipoToken.LPAREN, "("),
        (TipoToken.RPAREN, ")"),
        (TipoToken.EOF, None),
    ]
