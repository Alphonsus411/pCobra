from cobra.core import Lexer, TipoToken


def test_unicode_identifiers_extra():
    codigo = """var ma\u00f1ana = 1
var se\u00f1al = 2
var \u03bbambda = 3
var \u00e1rbol = 4"""
    lexer = Lexer(codigo)
    tokens = lexer.analizar_token()
    assert [(t.tipo, t.valor) for t in tokens] == [
        (TipoToken.VAR, 'var'),
        (TipoToken.IDENTIFICADOR, 'ma\u00f1ana'),
        (TipoToken.ASIGNAR, '='),
        (TipoToken.ENTERO, 1),
        (TipoToken.VAR, 'var'),
        (TipoToken.IDENTIFICADOR, 'se\u00f1al'),
        (TipoToken.ASIGNAR, '='),
        (TipoToken.ENTERO, 2),
        (TipoToken.VAR, 'var'),
        (TipoToken.IDENTIFICADOR, '\u03bbambda'),
        (TipoToken.ASIGNAR, '='),
        (TipoToken.ENTERO, 3),
        (TipoToken.VAR, 'var'),
        (TipoToken.IDENTIFICADOR, '\u00e1rbol'),
        (TipoToken.ASIGNAR, '='),
        (TipoToken.ENTERO, 4),
        (TipoToken.EOF, None),
    ]
