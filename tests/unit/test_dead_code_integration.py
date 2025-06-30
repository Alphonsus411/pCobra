from src.core.interpreter import InterpretadorCobra
from src.core.ast_nodes import (
    NodoFuncion,
    NodoRetorno,
    NodoAsignacion,
    NodoValor,
    NodoBucleMientras,
    NodoRomper,
    NodoCondicional,
    NodoLlamadaFuncion,
)


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
