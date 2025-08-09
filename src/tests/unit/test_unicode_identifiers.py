from cobra.core import Lexer, TipoToken


def test_unicode_identifiers():
    codigo = """var año = 1
var niño = 2
var Ωmega = 3"""
    lexer = Lexer(codigo)
    tokens = lexer.analizar_token()
    assert [(t.tipo, t.valor) for t in tokens] == [
        (TipoToken.VAR, 'var'),
        (TipoToken.IDENTIFICADOR, 'año'),
        (TipoToken.ASIGNAR, '='),
        (TipoToken.ENTERO, 1),
        (TipoToken.VAR, 'var'),
        (TipoToken.IDENTIFICADOR, 'niño'),
        (TipoToken.ASIGNAR, '='),
        (TipoToken.ENTERO, 2),
        (TipoToken.VAR, 'var'),
        (TipoToken.IDENTIFICADOR, 'Ωmega'),
        (TipoToken.ASIGNAR, '='),
        (TipoToken.ENTERO, 3),
        (TipoToken.EOF, None),
    ]
