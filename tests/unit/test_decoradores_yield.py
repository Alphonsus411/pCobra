from src.core.ast_nodes import (
    NodoFuncion,
    NodoDecorador,
    NodoYield,
    NodoImprimir,
    NodoValor,
    NodoIdentificador,
)
from src.cobra.transpilers.transpiler.to_python import TranspiladorPython


def test_transpilar_funcion_con_decorador():
    decorador = NodoDecorador(NodoIdentificador("decor"))
    func = NodoFuncion("saluda", [], [NodoImprimir(NodoValor("'hola'"))], [decorador])
    codigo = TranspiladorPython().generate_code([func])
    esperado = (
        "from src.core.nativos import *\n"
        "@decor\n"
        "def saluda():\n    print('hola')\n"
    )
    assert codigo == esperado


def test_transpilar_funcion_con_yield():
    func = NodoFuncion("generador", [], [NodoYield(NodoValor(1))])
    codigo = TranspiladorPython().generate_code([func])
    esperado = (
        "from src.core.nativos import *\n"
        "def generador():\n    yield 1\n"
    )
    assert codigo == esperado
