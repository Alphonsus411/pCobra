from src.cobra.lexico.lexer import Lexer, TipoToken


def test_lexer_metodo_atributo_tokens():
    tokens = Lexer("metodo atributo").analizar_token()
    tipos = [t.tipo for t in tokens if t.tipo != TipoToken.EOF]
    assert tipos == [TipoToken.METODO, TipoToken.ATRIBUTO]
