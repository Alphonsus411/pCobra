from core.ast_nodes import NodoAsignacion, NodoFuncion, NodoYield, NodoValor
from core.ast_nodes import NodoLlamadaFuncion
from core.interpreter import InterpretadorCobra


def test_interpretador_generador_simple():
    inter = InterpretadorCobra()
    funcion = NodoFuncion("gen", [], [NodoYield(NodoValor(1)), NodoYield(NodoValor(2))])
    inter.ejecutar_funcion(funcion)
    gen = inter.ejecutar_llamada_funcion(NodoLlamadaFuncion("gen", []))
    assert next(gen) == 1
    assert next(gen) == 2


def test_generador_limpia_contexto_exactamente_una_vez_en_finally():
    inter = InterpretadorCobra()
    inter.ejecutar_asignacion(NodoAsignacion("global_previa", NodoValor(7)))
    contextos_iniciales = len(inter.contextos)
    mem_contextos_iniciales = len(inter.mem_contextos)

    funcion = NodoFuncion("gen", [], [NodoYield(NodoValor(1))])
    inter.ejecutar_funcion(funcion)
    gen = inter.ejecutar_llamada_funcion(NodoLlamadaFuncion("gen", []))

    assert next(gen) == 1

    try:
        next(gen)
    except StopIteration:
        pass

    assert inter.obtener_variable("global_previa") == 7
    assert len(inter.contextos) == contextos_iniciales
    assert len(inter.mem_contextos) == mem_contextos_iniciales
