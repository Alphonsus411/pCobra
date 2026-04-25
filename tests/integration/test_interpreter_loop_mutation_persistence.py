from __future__ import annotations

from unittest.mock import patch

import pytest

from cobra.core import Token, TipoToken
from core.ast_nodes import (
    NodoAsignacion,
    NodoBucleMientras,
    NodoIdentificador,
    NodoOperacionBinaria,
    NodoValor,
)
from core.interpreter import InterpretadorCobra


@pytest.mark.integration
def test_mutacion_en_loop_persiste_entre_iteraciones_y_fuera_del_bucle() -> None:
    inter = InterpretadorCobra()
    inter.ejecutar_asignacion(NodoAsignacion("contador", NodoValor(0), declaracion=True))
    inter.ejecutar_asignacion(NodoAsignacion("ultimo", NodoValor(0), declaracion=True))

    condicion = NodoOperacionBinaria(
        NodoIdentificador("contador"),
        Token(TipoToken.MENORQUE, "<"),
        NodoValor(3),
    )
    cuerpo = [
        NodoAsignacion(
            "contador",
            NodoOperacionBinaria(
                NodoIdentificador("contador"),
                Token(TipoToken.SUMA, "+"),
                NodoValor(1),
            ),
        ),
        NodoAsignacion("ultimo", NodoIdentificador("contador")),
    ]

    with patch.object(
        InterpretadorCobra,
        "_asegurar_no_autorreferencia_asignacion",
        return_value=None,
    ):
        inter.ejecutar_mientras(NodoBucleMientras(condicion, cuerpo))

    assert inter.obtener_variable("contador") == 3
    assert inter.obtener_variable("ultimo") == 3
