import threading

import pytest
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
    interp.ejecutar_asignacion(NodoAsignacion("contador", NodoValor(0)))
    funcion = NodoFuncion(
        "trabajo",
        ["n"],
        [NodoAsignacion("contador", NodoIdentificador("n"))],
    )
    interp.ejecutar_funcion(funcion)

    hilos = [
        interp.ejecutar_hilo(NodoHilo(NodoLlamadaFuncion("trabajo", [NodoValor(i)])))
        for i in range(10)
    ]
    for h in hilos:
        h.join()

    assert interp.variables["contador"] == 0
    assert len(interp.contextos) == 1


def _registrar_nativa(interp, nombre, callback):
    interp.funciones_nativas[nombre] = callback


@pytest.mark.timeout(5)
@pytest.mark.parametrize("repeticion", range(5))
def test_dos_workers_alcanzan_barrera_sin_serializar_ejecucion(repeticion):
    """Falla con el bloqueo histórico: el primer worker rompe la barrera."""
    interp = InterpretadorCobra()
    barrera = threading.Barrier(2, timeout=1)
    alcanzados = []
    lock_resultados = threading.Lock()

    def sincronizar(etiqueta):
        barrera.wait()
        with lock_resultados:
            alcanzados.append(etiqueta)

    _registrar_nativa(interp, "sincronizar", sincronizar)
    interp.ejecutar_funcion(
        NodoFuncion(
            "trabajo",
            ["etiqueta"],
            [NodoLlamadaFuncion("sincronizar", [NodoIdentificador("etiqueta")])],
        )
    )

    hilos = [
        interp.ejecutar_hilo(
            NodoHilo(NodoLlamadaFuncion("trabajo", [NodoValor(etiqueta)]))
        )
        for etiqueta in ("a", "b")
    ]
    for hilo in hilos:
        hilo.join(timeout=2)

    assert not any(hilo.is_alive() for hilo in hilos)
    assert sorted(alcanzados) == ["a", "b"]
    assert len(interp.contextos) == len(interp.mem_contextos) == 1


@pytest.mark.timeout(5)
def test_workers_aislan_locales_y_preservan_referencias_lexicas():
    interp = InterpretadorCobra()
    barrera = threading.Barrier(2, timeout=1)
    compartido = []
    observados = {}
    lock_resultados = threading.Lock()

    def observar(etiqueta, valor):
        barrera.wait()
        compartido.append(etiqueta)
        with lock_resultados:
            observados[etiqueta] = valor

    interp.variables["compartido"] = compartido
    _registrar_nativa(interp, "observar", observar)
    interp.ejecutar_funcion(
        NodoFuncion(
            "local",
            ["etiqueta"],
            [
                NodoAsignacion(
                    "temporal", NodoIdentificador("etiqueta"), declaracion=True
                ),
                NodoLlamadaFuncion(
                    "observar",
                    [NodoIdentificador("etiqueta"), NodoIdentificador("temporal")],
                ),
            ],
        )
    )

    hilos = [
        interp.ejecutar_hilo(NodoHilo(NodoLlamadaFuncion("local", [NodoValor(valor)])))
        for valor in ("uno", "dos")
    ]
    for hilo in hilos:
        hilo.join(timeout=2)

    assert observados == {"uno": "uno", "dos": "dos"}
    assert sorted(compartido) == ["dos", "uno"]
    assert "temporal" not in interp.variables
    assert len(interp.contextos) == len(interp.mem_contextos) == 1


@pytest.mark.timeout(5)
def test_excepcion_de_worker_no_corrompe_pilas(monkeypatch):
    interp = InterpretadorCobra()
    capturadas = []
    ocurrio = threading.Event()

    def capturar(args):
        capturadas.append(args.exc_value)
        ocurrio.set()

    def fallar():
        raise RuntimeError("fallo determinista")

    monkeypatch.setattr(threading, "excepthook", capturar)
    _registrar_nativa(interp, "fallar", fallar)
    interp.ejecutar_funcion(
        NodoFuncion("worker", [], [NodoLlamadaFuncion("fallar", [])])
    )

    hilo = interp.ejecutar_hilo(NodoHilo(NodoLlamadaFuncion("worker", [])))
    assert ocurrio.wait(timeout=2)
    hilo.join(timeout=2)

    assert [str(exc) for exc in capturadas] == ["fallo determinista"]
    assert len(interp.contextos) == len(interp.mem_contextos) == 1
    assert interp._call_depth == 0
    assert not interp._eval_stack
