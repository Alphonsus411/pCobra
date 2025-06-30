from src.cobra.lexico.lexer import Lexer
from src.cobra.parser.parser import Parser
from src.core.ast_nodes import NodoFuncion, NodoDecorador, NodoIdentificador


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
