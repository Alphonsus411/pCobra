from src.core.lexer import Lexer, TipoToken


def test_lexer_asignacion_variable():
    codigo = 'var x = holobit([0.8, -0.5, 1.2])'
    lexer = Lexer(codigo)
    tokens = lexer.analizar_token()

    assert tokens[0].tipo == TipoToken.VAR
    assert tokens[1].tipo == TipoToken.IDENTIFICADOR
    assert tokens[1].valor == 'x'
    assert tokens[2].tipo == TipoToken.ASIGNAR
    assert tokens[3].tipo == TipoToken.HOLOBIT
    assert tokens[4].tipo == TipoToken.LPAREN
    assert tokens[5].tipo == TipoToken.LBRACKET  # Corchete de apertura
    assert tokens[6].tipo == TipoToken.FLOTANTE
    assert tokens[6].valor == 0.8  # Cambiado de '0.8' a 0.8 (número)


def test_lexer_transformacion_holobit():
    codigo = 'transformar(holobit([1.0, 2.0, -0.5]), "rotar", 45)'

    lexer = Lexer(codigo)
    tokens = lexer.analizar_token()

    assert tokens[0].tipo == TipoToken.TRANSFORMAR
    assert tokens[1].tipo == TipoToken.LPAREN
    assert tokens[2].tipo == TipoToken.HOLOBIT
    assert tokens[3].tipo == TipoToken.LPAREN
    assert tokens[4].tipo == TipoToken.LBRACKET  # Corchete de apertura
    assert tokens[5].tipo == TipoToken.FLOTANTE
    assert tokens[5].valor == 1.0  # Cambiado de '1.0' a 1.0 (número)
