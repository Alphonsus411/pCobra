import json
from cobra.core import Token, TipoToken
from cobra.core.lark_parser import LarkParser


def test_tokens_to_source_cadenas_comillas_y_salto_linea():
    """Verifica que las cadenas se escapen con json.dumps y otros tokens con repr."""
    cadena_valor = 'hola "cobra"\nfin'
    otro_valor = 'linea1\nlinea2'
    tokens = [
        Token(TipoToken.CADENA, cadena_valor),
        Token(TipoToken.IDENTIFICADOR, otro_valor),
        Token(TipoToken.EOF, None),
    ]
    parser = LarkParser(tokens)
    esperado = f"{json.dumps(cadena_valor)} {repr(otro_valor)}"
    assert parser._tokens_to_source() == esperado

