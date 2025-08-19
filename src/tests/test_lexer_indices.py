from cobra.core.lexer import Lexer, TipoToken


def test_peek_and_state_after_tokenizar():
    codigo = "var x = 5"
    lexer = Lexer(codigo)

    # tokenizar genera la lista de tokens y reinicia el índice
    tokens = lexer.tokenizar()
    assert tokens[0].tipo == TipoToken.VAR

    # peek no debe consumir el primer token
    primer_peek = lexer.peek()
    assert primer_peek is not None
    assert primer_peek.tipo == TipoToken.VAR

    # siguiente_token devuelve el mismo token observado por peek
    primer_token = lexer.siguiente_token()
    assert primer_token == primer_peek

    # el siguiente token debe ser el identificador "x"
    segundo_token = lexer.siguiente_token()
    assert segundo_token.tipo == TipoToken.IDENTIFICADOR

    # retroceder permite volver a leer el identificador
    lexer.retroceder()
    assert lexer.siguiente_token() == segundo_token

    # guardar y restaurar estado alrededor del operador de asignación
    estado = lexer.guardar_estado()
    tercer_token = lexer.siguiente_token()
    assert tercer_token.tipo == TipoToken.ASIGNAR
    lexer.restaurar_estado(estado)
    assert lexer.siguiente_token() == tercer_token

    # aún deben quedar tokens por leer (el número 5 y EOF)
    assert lexer.hay_mas_tokens()
