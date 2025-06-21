from src.core.lexer import Token, TipoToken
from src.core.parser import Parser, NodoHolobit


def test_parser_holobit():
    tokens = [
        Token(TipoToken.HOLOBIT, 'holobit'),
        Token(TipoToken.LPAREN, '('),
        Token(TipoToken.LBRACKET, '['),
        Token(TipoToken.FLOTANTE, 0.8),
        Token(TipoToken.COMA, ','),
        Token(TipoToken.FLOTANTE, -0.5),  # Cambiado a un flotante negativo
        Token(TipoToken.COMA, ','),
        Token(TipoToken.FLOTANTE, 1.2),
        Token(TipoToken.RBRACKET, ']'),
        Token(TipoToken.RPAREN, ')'),
        Token(TipoToken.EOF, None)
    ]

    parser = Parser(tokens)
    arbol = parser.parsear()

    assert isinstance(arbol[0], NodoHolobit), "Se esperaba un nodo de tipo NodoHolobit"
    assert len(arbol[0].valores) == 3, "El holobit debe contener 3 valores"
    assert arbol[0].valores[0].valor == 0.8, "El primer valor del holobit debe ser 0.8"
    assert arbol[0].valores[1].valor == -0.5, "El segundo valor del holobit debe ser -0.5"
    assert arbol[0].valores[2].valor == 1.2, "El tercer valor del holobit debe ser 1.2"

