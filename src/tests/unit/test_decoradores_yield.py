from core.ast_nodes import (
    NodoFuncion,
    NodoDecorador,
    NodoYield,
    NodoImprimir,
    NodoValor,
    NodoIdentificador,
)
from cobra.transpilers.transpiler.to_python import TranspiladorPython
from cobra.transpilers.import_helper import get_standard_imports

IMPORTS = get_standard_imports("python")


def test_transpilar_funcion_con_decorador():
    decorador = NodoDecorador(NodoIdentificador("decor"))
    func = NodoFuncion("saluda", [], [NodoImprimir(NodoValor("'hola'"))], [decorador])
    codigo = TranspiladorPython().generate_code([func])
    esperado = (
        IMPORTS
        "@decor\n"
        "def saluda():\n    print('hola')\n"
    )
    assert codigo == esperado


def test_transpilar_funcion_con_yield():
    func = NodoFuncion("generador", [], [NodoYield(NodoValor(1))])
    codigo = TranspiladorPython().generate_code([func])
    esperado = (
        IMPORTS
        "def generador():\n    yield 1\n"
    )
    assert codigo == esperado
