from cobra.lexico.lexer import Token, TipoToken
from cobra.parser.parser import Parser


def test_parser_para_mas_de_mil_sentencias():
    tokens = [
        Token(TipoToken.PARA, 'para'),
        Token(TipoToken.IDENTIFICADOR, 'i'),
        Token(TipoToken.IN, 'in'),
        Token(TipoToken.IDENTIFICADOR, 'lista'),
        Token(TipoToken.DOSPUNTOS, ':'),
    ]
    tokens.extend([Token(TipoToken.PASAR, 'pasar') for _ in range(1001)])
    tokens.extend([
        Token(TipoToken.FIN, 'fin'),
        Token(TipoToken.EOF, None),
    ])

    parser = Parser(tokens)
    ast = parser.parsear()

    assert len(ast[0].cuerpo) == 1001
