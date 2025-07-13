from cobra.lexico.lexer import Lexer, TipoToken


def test_unicode_comments_removed():
    codigo = """
    # пример
    var x = 1
    // مثال
    imprimir(x)
    /* مثال */
    """
    tokens = Lexer(codigo).analizar_token()

    assert [(t.tipo, t.valor) for t in tokens] == [
        (TipoToken.VAR, "var"),
        (TipoToken.IDENTIFICADOR, "x"),
        (TipoToken.ASIGNAR, "="),
        (TipoToken.ENTERO, 1),
        (TipoToken.IMPRIMIR, "imprimir"),
        (TipoToken.LPAREN, "("),
        (TipoToken.IDENTIFICADOR, "x"),
        (TipoToken.RPAREN, ")"),
        (TipoToken.EOF, None),
    ]
