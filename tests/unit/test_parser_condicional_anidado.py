from pathlib import Path

import pytest
from cobra.core import Lexer
from cobra.core import Parser
from core.ast_nodes import NodoCondicional, NodoImprimir

DATA_DIR = Path(__file__).resolve().parent.parent / "data"


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


def test_parser_cascada_sino_si():
    codigo = (DATA_DIR / "condicional_sino_si.cobra").read_text(encoding="utf-8")
    tokens = Lexer(codigo).analizar_token()
    ast = Parser(tokens).parsear()

    assert isinstance(ast[0], NodoCondicional)
    assert len(ast[0].bloque_sino) == 1
    nodo_elif = ast[0].bloque_sino[0]
    assert isinstance(nodo_elif, NodoCondicional)
    assert len(nodo_elif.bloque_si) == 1
    assert nodo_elif.bloque_sino
    assert isinstance(nodo_elif.bloque_sino[0], NodoImprimir)
