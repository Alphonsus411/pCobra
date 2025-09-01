import pytest
from cobra.core import Lexer
from cobra.core import Parser, ParserError


def test_sugerencia_palabra_clave():
    codigo = "imprmir 1"
    tokens = Lexer(codigo).analizar_token()
    parser = Parser(tokens)
    with pytest.raises(ParserError, match="¿Quiso decir 'imprimir'?"):
        parser.parsear()

