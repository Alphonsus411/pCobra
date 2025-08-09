from cobra.core import Lexer
from cobra.core import Parser
from core.ast_nodes import NodoFuncion, NodoClase, NodoDecorador, NodoIdentificador


def test_parser_funcion_con_decorador():
    codigo = """@decor\nfunc saludo():\n    fin"""
    tokens = Lexer(codigo).analizar_token()
    ast = Parser(tokens).parsear()
    assert len(ast) == 1
    nodo = ast[0]
    assert isinstance(nodo, NodoFuncion)
    assert len(nodo.decoradores) == 1
    decor = nodo.decoradores[0]
    assert isinstance(decor, NodoDecorador)
    assert isinstance(decor.expresion, NodoIdentificador)
    assert decor.expresion.nombre == "decor"


def test_parser_clase_con_decorador():
    codigo = """@decor\nclase C:\n    pasar\nfin"""
    tokens = Lexer(codigo).analizar_token()
    ast = Parser(tokens).parsear()
    assert len(ast) == 1
    nodo = ast[0]
    assert isinstance(nodo, NodoClase)
    assert len(nodo.decoradores) == 1
    decor = nodo.decoradores[0]
    assert isinstance(decor, NodoDecorador)
    assert isinstance(decor.expresion, NodoIdentificador)
    assert decor.expresion.nombre == "decor"
