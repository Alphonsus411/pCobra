from cobra.lexico.lexer import Lexer
from cobra.parser.parser import Parser
from core.ast_nodes import NodoSwitch, NodoCase, NodoImprimir


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
