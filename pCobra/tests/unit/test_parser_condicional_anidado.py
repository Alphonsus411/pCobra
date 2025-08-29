import pytest
from cobra.core import Lexer
from cobra.core import Parser
from core.ast_nodes import NodoCondicional


def test_parser_condicional_si_en_sino():
    codigo = '''
    si x > 0:
        imprimir(x)
    sino:
        si x < 0:
            imprimir(x)
        fin
    fin
    '''
    tokens = Lexer(codigo).analizar_token()
    ast = Parser(tokens).parsear()

    assert isinstance(ast[0], NodoCondicional)
    assert isinstance(ast[0].bloque_sino[0], NodoCondicional)
