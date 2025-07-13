import pytest
from core.interpreter import InterpretadorCobra
from core.ast_nodes import NodoAsignacion, NodoValor, NodoFuncion, NodoLlamadaFuncion

def test_asignaciones_intensivas_libera_memoria():
    inter = InterpretadorCobra()
    for i in range(500):
        inter.ejecutar_asignacion(NodoAsignacion(f"v{i}", NodoValor(i)))
    assert len(inter.mem_contextos[0]) == 500

    # Reasignar algunas variables para liberar memoria
    for i in range(250):
        inter.ejecutar_asignacion(NodoAsignacion(f"v{i}", NodoValor(i+1)))
    assert len(inter.mem_contextos[0]) == 500  # mismo número, pero se liberó y reasignó


def test_evolucion_durante_programa_largo():
    inter = InterpretadorCobra()
    for i in range(1200):
        inter.solicitar_memoria(1)
    assert inter.gestor_memoria.generacion >= 1

