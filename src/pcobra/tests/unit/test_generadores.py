from core.ast_nodes import NodoFuncion, NodoYield, NodoValor
from core.ast_nodes import NodoLlamadaFuncion
from core.interpreter import InterpretadorCobra


def test_interpretador_generador_simple():
    inter = InterpretadorCobra()
    funcion = NodoFuncion("gen", [], [NodoYield(NodoValor(1)), NodoYield(NodoValor(2))])
    inter.ejecutar_funcion(funcion)
    gen = inter.ejecutar_llamada_funcion(NodoLlamadaFuncion("gen", []))
    assert next(gen) == 1
    assert next(gen) == 2
