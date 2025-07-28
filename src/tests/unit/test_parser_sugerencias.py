import pytest
from cobra.lexico.lexer import Lexer
from cobra.parser.parser import Parser


def test_sugerencia_palabra_clave():
    codigo = "imprmir 1"
    tokens = Lexer(codigo).analizar_token()
    parser = Parser(tokens)
    with pytest.raises(SyntaxError, match="¿Quiso decir 'imprimir'?"):
        parser.parsear()

