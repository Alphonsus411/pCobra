from src.cobra.lexico.lexer import Lexer
from src.cobra.parser.parser import Parser
from src.core.ast_nodes import NodoClase, NodoMetodo, NodoAsignacion, NodoAtributo, NodoImprimir


def test_parser_metodo_keyword():
    codigo = """
    clase Persona:
        metodo saludar(self):
            fin
    fin
    """
    ast = Parser(Lexer(codigo).analizar_token()).parsear()
    clase = ast[0]
    assert isinstance(clase, NodoClase)
    assert clase.metodos[0].nombre == "saludar"


def test_parser_atributo_asignacion():
    codigo = "atributo obj nombre = 1"
    ast = Parser(Lexer(codigo).analizar_token()).parsear()
    asign = ast[0]
    assert isinstance(asign, NodoAsignacion)
    assert isinstance(asign.variable, NodoAtributo)
    assert asign.variable.objeto.nombre == "obj"
    assert asign.variable.nombre == "nombre"


def test_parser_atributo_expresion():
    codigo = "imprimir(atributo obj nombre)"
    ast = Parser(Lexer(codigo).analizar_token()).parsear()
    imp = ast[0]
    assert isinstance(imp, NodoImprimir)
    attr = imp.expresion
    assert isinstance(attr, NodoAtributo)
    assert attr.nombre == "nombre"
