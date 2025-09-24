from cobra.core import Lexer
from cobra.core import Parser
from pcobra.core.ast_nodes import NodoClase, NodoMetodo


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


def test_parser_declaracion_estructura():
    codigo = """
    estructura Registro:
        pasar
    fin
    """
    tokens = Lexer(codigo).analizar_token()
    ast = Parser(tokens).parsear()
    assert len(ast) == 1
    clase = ast[0]
    assert isinstance(clase, NodoClase)
    assert clase.nombre == "Registro"


def test_parser_declaracion_registro():
    codigo = """
    registro Archivo:
        pasar
    fin
    """
    tokens = Lexer(codigo).analizar_token()
    ast = Parser(tokens).parsear()
    assert len(ast) == 1
    clase = ast[0]
    assert isinstance(clase, NodoClase)
    assert clase.nombre == "Archivo"


def test_parser_advertencia_alias_clase():
    codigo = """
    clase Uno:
        pasar
    fin

    estructura Dos:
        pasar
    fin
    """
    tokens = Lexer(codigo).analizar_token()
    parser = Parser(tokens)
    parser.parsear()
    assert parser.advertencias, "Se esperaba una advertencia por mezclar alias"
    mensaje = parser.advertencias[0]
    assert "clases" in mensaje
    assert "'clase'" in mensaje and "'estructura'" in mensaje


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


def test_parser_clase_alias_async_choque_nombres():
    codigo = """
    clase Gestor:
        asincronico metodo entrar_async(self):
            pasar
        fin
        asincronico metodo __aenter__(self):
            pasar
        fin
    fin
    """
    tokens = Lexer(codigo).analizar_token()
    parser = Parser(tokens)
    ast = parser.parsear()
    clase = ast[0]
    assert isinstance(clase, NodoClase)
    metodos = [n for n in clase.metodos if isinstance(n, NodoMetodo)]
    assert len(metodos) == 2
    nombres = [metodo.nombre for metodo in metodos]
    assert nombres == ["__aenter__", "__aenter__"]
    assert len(parser.advertencias) == 1
    mensaje = parser.advertencias[0]
    assert "Choque de nombres" in mensaje
    assert "entrar_async" in mensaje and "__aenter__" in mensaje
