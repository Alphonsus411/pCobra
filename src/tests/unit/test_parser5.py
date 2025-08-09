import pytest
from cobra.core import Lexer
from cobra.core import Parser
from core.ast_nodes import NodoPara, NodoImprimir, NodoFuncion, NodoIdentificador

def test_declaracion_para():
    """Prueba una declaración de bucle 'para'."""
    codigo = """
    para i in range(0, 10):
        imprimir(i)
    fin
    """
    tokens = Lexer(codigo).tokenizar()
    parser = Parser(tokens)
    ast = parser.parsear()

    assert len(ast) == 1
    nodo_para = ast[0]
    assert isinstance(nodo_para, NodoPara)
    assert nodo_para.variable == "i"
    assert nodo_para.iterable.valor == "range(0, 10)"  # O ajusta según cómo se represente el iterable
    assert len(nodo_para.cuerpo) == 1
    assert isinstance(nodo_para.cuerpo[0], NodoImprimir)
    assert isinstance(nodo_para.cuerpo[0].expresion, NodoIdentificador)
    assert nodo_para.cuerpo[0].expresion.nombre == "i"


def test_declaracion_imprimir():
    """Prueba una declaración de impresión."""
    codigo = """
    imprimir("Hola, Cobra!")
    """
    tokens = Lexer(codigo).tokenizar()
    parser = Parser(tokens)
    ast = parser.parsear()

    assert len(ast) == 1
    nodo_imprimir = ast[0]
    assert isinstance(nodo_imprimir, NodoImprimir)
    assert nodo_imprimir.expresion.valor == "Hola, Cobra!"


def test_declaracion_imprimir_sin_parentesis():
    """Prueba la impresión sin paréntesis."""
    codigo = """
    imprimir x
    """
    tokens = Lexer(codigo).tokenizar()
    parser = Parser(tokens)
    ast = parser.parsear()

    assert len(ast) == 1
    nodo_imprimir = ast[0]
    assert isinstance(nodo_imprimir, NodoImprimir)
    assert isinstance(nodo_imprimir.expresion, NodoIdentificador)
    assert nodo_imprimir.expresion.nombre == "x"


def test_funcion_y_para():
    """Prueba una función que incluye un bucle 'para'."""
    codigo = """
    func sumar_rangos():
        para i in range(0, 5):
            imprimir(i)
        fin
    fin
    """
    tokens = Lexer(codigo).tokenizar()
    parser = Parser(tokens)
    ast = parser.parsear()

    assert len(ast) == 1
    nodo_funcion = ast[0]
    assert isinstance(nodo_funcion, NodoFuncion)
    assert nodo_funcion.nombre == "sumar_rangos"
    assert len(nodo_funcion.cuerpo) == 1

    nodo_para = nodo_funcion.cuerpo[0]
    assert isinstance(nodo_para, NodoPara)
    assert nodo_para.variable == "i"
    assert nodo_para.iterable.valor == "range(0, 5)"  # Ajusta según representación
    assert len(nodo_para.cuerpo) == 1

    nodo_imprimir = nodo_para.cuerpo[0]
    assert isinstance(nodo_imprimir, NodoImprimir)
    assert isinstance(nodo_imprimir.expresion, NodoIdentificador)
    assert nodo_imprimir.expresion.nombre == "i"
