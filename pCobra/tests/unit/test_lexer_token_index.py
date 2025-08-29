from cobra.core import Lexer, TipoToken


def test_peek_and_navigation_after_tokenizar():
    codigo = "var x = 1"
    lexer = Lexer(codigo)
    lexer.tokenizar()

    # peek debe mostrar el primer token sin consumirlo
    primer = lexer.peek()
    assert primer.tipo == TipoToken.VAR
    assert lexer.hay_mas_tokens()

    # consumir y navegar por los tokens
    assert lexer.siguiente_token().tipo == TipoToken.VAR
    assert lexer.siguiente_token().tipo == TipoToken.IDENTIFICADOR

    # retroceder y volver a leer el identificador
    lexer.retroceder()
    assert lexer.peek().tipo == TipoToken.IDENTIFICADOR

    # guardar y restaurar estado
    estado = lexer.guardar_estado()
    assert lexer.siguiente_token().tipo == TipoToken.IDENTIFICADOR
    lexer.restaurar_estado(estado)
    assert lexer.siguiente_token().tipo == TipoToken.IDENTIFICADOR

    # consumir el resto de tokens hasta EOF
    ultimo = None
    while lexer.hay_mas_tokens():
        ultimo = lexer.siguiente_token()
    assert ultimo is not None and ultimo.tipo == TipoToken.EOF
    assert not lexer.hay_mas_tokens()
    assert lexer.siguiente_token() is None
