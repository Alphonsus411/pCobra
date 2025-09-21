from cobra.core import Lexer
from cobra.core import Parser
from core.ast_nodes import NodoClase, NodoMetodo


def test_parser_declaracion_clase():
    codigo = """
    clase Persona:
        func saludar(self):
            fin
    fin
    """
    tokens = Lexer(codigo).analizar_token()
    ast = Parser(tokens).parsear()
    assert len(ast) == 1
    clase = ast[0]
    assert isinstance(clase, NodoClase)
    assert clase.nombre == "Persona"
    assert len(clase.metodos) == 1
    metodo = clase.metodos[0]
    assert isinstance(metodo, NodoMetodo)
    assert metodo.nombre == "saludar"


def test_parser_clase_alias_choque_nombres():
    codigo = """
    clase Persona:
        metodo inicializar(self):
            pasar
        fin
        metodo __init__(self):
            pasar
        fin
    fin
    """
    tokens = Lexer(codigo).analizar_token()
    parser = Parser(tokens)
    ast = parser.parsear()
    clase = ast[0]
    assert isinstance(clase, NodoClase)
    assert len(clase.metodos) == 2
    nombres = [metodo.nombre for metodo in clase.metodos]
    assert nombres == ["__init__", "__init__"]
    assert len(parser.advertencias) == 1
    mensaje = parser.advertencias[0]
    assert "Choque de nombres" in mensaje
    assert "inicializar" in mensaje and "__init__" in mensaje
