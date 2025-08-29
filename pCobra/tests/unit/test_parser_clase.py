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
