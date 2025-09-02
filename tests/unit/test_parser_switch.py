from cobra.core import Lexer
from cobra.core import Parser
from core.ast_nodes import NodoSwitch, NodoCase, NodoImprimir, NodoGuard, NodoPattern


def test_parser_switch():
    codigo = """
    switch x:
        case 1:
            imprimir(1)
        case 2:
            imprimir(2)
        sino:
            imprimir(0)
    fin
    """
    ast = Parser(Lexer(codigo).analizar_token()).parsear()
    nodo = ast[0]
    assert isinstance(nodo, NodoSwitch)
    assert len(nodo.casos) == 2
    assert isinstance(nodo.casos[0], NodoCase)
    assert len(nodo.por_defecto) == 1
    assert isinstance(nodo.por_defecto[0], NodoImprimir)


def test_parser_switch_patrones_guardia():
    codigo = """
    switch punto:
        case (x, (y, _)) si x > y:
            imprimir(x)
        sino:
            imprimir(0)
    fin
    """
    ast = Parser(Lexer(codigo).analizar_token()).parsear()
    nodo = ast[0]
    caso = nodo.casos[0]
    assert isinstance(caso.valor, NodoGuard)
    patron = caso.valor.patron
    assert isinstance(patron, NodoPattern)
    assert isinstance(patron.valor, list) and len(patron.valor) == 2
    interno = patron.valor[1]
    assert isinstance(interno.valor, list)
    assert interno.valor[1].valor == "_"
