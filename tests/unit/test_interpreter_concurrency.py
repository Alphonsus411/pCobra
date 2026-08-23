import pytest
import threading
from pcobra.core.interpreter import InterpretadorCobra
from pcobra.core.ast_nodes import (
    NodoAsignacion,
    NodoValor,
    NodoFuncion,
    NodoHilo,
    NodoLlamadaFuncion,
    NodoIdentificador,
)


@pytest.mark.timeout(5)
def test_hilos_preservan_variables_globales_concurrentes():
    interp = InterpretadorCobra()
    interp.ejecutar_asignacion(
        NodoAsignacion('contador', NodoValor(0), declaracion=True)
    )
    funcion = NodoFuncion(
        'trabajo',
        ['n'],
        [NodoAsignacion('contador', NodoIdentificador('n'))],
    )
    interp.ejecutar_funcion(funcion)

    hilos = [
        interp.ejecutar_hilo(
            NodoHilo(NodoLlamadaFuncion('trabajo', [NodoValor(i)]))
        )
        for i in range(10)
    ]
    for h in hilos:
        h.join()

    assert interp.variables['contador'] == 0
    assert len(interp.contextos) == 1


@pytest.mark.timeout(5)
def test_hilos_cobra_pueden_sincronizarse_sin_serializarse():
    interp = InterpretadorCobra()
    barrera = threading.Barrier(2)
    interp.funciones_nativas["esperar"] = lambda: barrera.wait(timeout=2)
    interp.ejecutar_funcion(
        NodoFuncion("trabajo", [], [NodoLlamadaFuncion("esperar", [])])
    )

    hilos = [
        interp.ejecutar_hilo(NodoHilo(NodoLlamadaFuncion("trabajo", [])))
        for _ in range(2)
    ]
    for hilo in hilos:
        hilo.join(timeout=3)

    assert all(not hilo.is_alive() for hilo in hilos)
    assert barrera.n_waiting == 0
    assert not barrera.broken
