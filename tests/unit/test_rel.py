"""Pruebas para el contexto temporal ``rel`` de la librería estándar."""

from __future__ import annotations

import time

from pcobra.standard_library.util import rel


class Demo:
    """Objeto auxiliar para evaluar cambios temporales."""

    def __init__(self) -> None:
        self.valor = 1
        self.activo = True


def test_rel_restaura_tras_duracion() -> None:
    """Verifica que ``rel`` aplica y revierte cambios tras un intervalo fijo."""

    demo = Demo()

    with rel(demo, {"valor": 99}, duracion=0.05):
        assert demo.valor == 99

        # Una espera superior a la duración garantiza la ejecución del temporizador.
        time.sleep(0.15)

        assert demo.valor == 1

    assert demo.valor == 1


def test_rel_condicional_aplica_y_revierte() -> None:
    """Comprueba que la condición controla la aplicación de los cambios."""

    demo = Demo()

    def condicion(objeto: Demo) -> bool:
        return objeto.activo

    with rel(demo, {"valor": 42}, condicion=condicion):
        assert demo.valor == 42

        # Si la condición deja de cumplirse, el valor debe volver al original
        # al finalizar el contexto.
        demo.activo = False

    assert demo.valor == 1

    # Con la condición desactivada ya no deberían aplicarse modificaciones.
    with rel(demo, {"valor": 17}, condicion=condicion):
        assert demo.valor == 1

    assert demo.valor == 1
