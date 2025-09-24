import pytest

from cobra.core import Lexer
from cobra.core import Parser
from pcobra.cobra.core.utils import ALIAS_METODOS_ESPECIALES
from pcobra.core.ast_nodes import (
    NodoClase,
    NodoMetodo,
    NodoFuncion,
    NodoAsignacion,
    NodoAtributo,
    NodoImprimir,
)


def test_parser_metodo_keyword():
    codigo = """
    clase Persona:
        metodo saludar(self):
            fin
    fin
    """
    parser = Parser(Lexer(codigo).analizar_token())
    ast = parser.parsear()
    clase = ast[0]
    assert isinstance(clase, NodoClase)
    assert clase.metodos[0].nombre == "saludar"
    assert parser.advertencias == []


def test_parser_metodo_alias_especial():
    codigo = """
    clase Persona:
        metodo inicializar(self):
            pasar
        fin
    fin
    """
    tokens = Lexer(codigo).analizar_token()
    parser = Parser(tokens)
    ast = parser.parsear()
    clase = ast[0]
    metodo = clase.metodos[0]
    assert metodo.nombre == "__init__"
    assert metodo.nombre_original == "inicializar"
    assert parser.advertencias == []


def test_parser_metodo_alias_texto():
    codigo = """
    clase Persona:
        metodo texto(self):
            pasar
        fin
    fin
    """
    parser = Parser(Lexer(codigo).analizar_token())
    clase = parser.parsear()[0]
    metodo = clase.metodos[0]
    assert metodo.nombre == "__str__"
    assert metodo.nombre_original == "texto"
    assert parser.advertencias == []


def test_parser_metodo_alias_async():
    codigo = """
    clase Gestor:
        asincronico metodo entrar_async(self):
            pasar
        fin
    fin
    """
    parser = Parser(Lexer(codigo).analizar_token())
    clase = parser.parsear()[0]
    metodo = clase.metodos[0]
    assert metodo.nombre == "__aenter__"
    assert metodo.nombre_original == "entrar_async"
    assert metodo.asincronica is True
    assert parser.advertencias == []


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


def test_parser_funcion_alias_especial():
    codigo = """
    func texto():
        pasar
    fin
    """
    parser = Parser(Lexer(codigo).analizar_token())
    ast = parser.parsear()
    funcion = ast[0]
    assert isinstance(funcion, NodoFuncion)
    assert funcion.nombre == "__str__"
    assert funcion.nombre_original == "texto"
    assert parser.advertencias == []


@pytest.mark.parametrize(
    ("alias", "nombre_dunder"),
    sorted(ALIAS_METODOS_ESPECIALES.items()),
)
def test_parser_metodo_alias_tabla(alias, nombre_dunder):
    prefijo = "asincronico " if alias.endswith("_async") else ""
    codigo = f"""
    clase Ejemplo:
        {prefijo}metodo {alias}(self):
            pasar
        fin
    fin
    """
    parser = Parser(Lexer(codigo).analizar_token())
    clase = parser.parsear()[0]
    metodo = clase.metodos[0]
    assert isinstance(metodo, NodoMetodo)
    assert metodo.nombre == nombre_dunder
    assert metodo.nombre_original == alias
    if alias.endswith("_async"):
        assert metodo.asincronica is True
    else:
        assert metodo.asincronica is False
    assert parser.advertencias == []
