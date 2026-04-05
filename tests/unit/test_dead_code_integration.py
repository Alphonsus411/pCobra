from core.interpreter import InterpretadorCobra
from core.optimizations import remove_dead_code
from core.ast_nodes import (
    NodoFuncion,
    NodoRetorno,
    NodoAsignacion,
    NodoValor,
    NodoBucleMientras,
    NodoRomper,
    NodoCondicional,
    NodoLlamadaFuncion,
)
import pytest


def test_ejecucion_sin_instrucciones_post_return():
    ast = [
        NodoFuncion(
            "f",
            [],
            [NodoRetorno(NodoValor(1)), NodoAsignacion("x", NodoValor(2))],
        ),
        NodoLlamadaFuncion("f", []),
    ]
    interpreter = InterpretadorCobra()
    interpreter.ejecutar_ast(ast)
    assert "x" not in interpreter.variables


def test_ejecucion_sin_instrucciones_post_break():
    ast = [
        NodoBucleMientras(
            NodoValor(True),
            [NodoRomper(), NodoAsignacion("x", NodoValor(1))],
        )
    ]
    interpreter = InterpretadorCobra()
    interpreter.ejecutar_ast(ast)
    assert "x" not in interpreter.variables


def test_condicional_constante():
    ast = [
        NodoCondicional(
            NodoValor(False),
            [NodoAsignacion("x", NodoValor(1))],
            [NodoAsignacion("y", NodoValor(2))],
        )
    ]
    interpreter = InterpretadorCobra()
    interpreter.ejecutar_ast(ast)
    assert "x" not in interpreter.variables
    assert interpreter.variables.get("y") == 2


@pytest.mark.parametrize(
    ("condicion_literal", "valor_esperado"),
    [(True, 1), (False, 2)],
)
def test_remove_dead_code_colapsa_condicional_literal_booleano(
    condicion_literal, valor_esperado
):
    ast = [
        NodoCondicional(
            NodoValor(condicion_literal),
            [NodoAsignacion("x", NodoValor(1))],
            [NodoAsignacion("x", NodoValor(2))],
        )
    ]

    optimizado = remove_dead_code(ast)

    assert len(optimizado) == 1
    assert isinstance(optimizado[0], NodoAsignacion)
    assert optimizado[0].valor.valor == valor_esperado


@pytest.mark.parametrize("valor_no_booleano", [5, "hola"])
def test_remove_dead_code_no_colapsa_condicional_literal_no_booleano_strict_boolean_sin_truthiness(
    valor_no_booleano,
):
    ast = [
        NodoCondicional(
            NodoValor(valor_no_booleano),
            [NodoAsignacion("x", NodoValor(1))],
            [NodoAsignacion("x", NodoValor(2))],
        )
    ]

    optimizado = remove_dead_code(ast)

    assert len(optimizado) == 1
    assert isinstance(optimizado[0], NodoCondicional)
