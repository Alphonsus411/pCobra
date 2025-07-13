import pytest
from core.interpreter import InterpretadorCobra
from core.ast_nodes import (
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
    interp.ejecutar_asignacion(NodoAsignacion('contador', NodoValor(0)))
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
