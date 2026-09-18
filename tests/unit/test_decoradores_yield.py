from pcobra.core.ast_nodes import (
    NodoFuncion,
    NodoDecorador,
    NodoYield,
    NodoImprimir,
    NodoValor,
    NodoIdentificador,
)
from pcobra.cobra.transpilers.transpiler.to_python import TranspiladorPython
from pcobra.cobra.transpilers.import_helper import get_standard_imports
from pcobra.cobra.core.lexer import Lexer
from pcobra.cobra.core.parser import Parser

IMPORTS = get_standard_imports("python")


def test_transpilar_funcion_con_decorador():
    decorador = NodoDecorador(NodoIdentificador("decor"))
    func = NodoFuncion("saluda", [], [NodoImprimir(NodoValor("hola"))], [decorador])
    codigo = TranspiladorPython().generate_code([func])
    esperado = IMPORTS + "@decor\n" + "def saluda():\n    print('hola')\n"
    assert codigo == esperado


def test_transpilar_funcion_con_yield():
    func = NodoFuncion("generador", [], [NodoYield(NodoValor(1))])
    codigo = TranspiladorPython().generate_code([func])
    esperado = IMPORTS + "def generador():\n    yield 1\n"
    assert codigo == esperado


def test_parsear_sentencia_yield_desde_codigo_fuente():
    ast = Parser(Lexer("yield 1").tokenizar()).parsear()

    assert len(ast) == 1
    assert isinstance(ast[0], NodoYield)
    assert ast[0].expresion == NodoValor(1)


def test_generar_no_se_interpreta_como_sentencia_yield():
    ast = Parser(Lexer("generar 1").tokenizar()).parsear()

    assert not any(isinstance(nodo, NodoYield) for nodo in ast)
