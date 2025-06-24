from src.cobra.transpilers.transpiler.to_asm import TranspiladorASM
from src.core.ast_nodes import (
    NodoAsignacion,
    NodoCondicional,
    NodoBucleMientras,
    NodoFuncion,
    NodoLlamadaFuncion,
    NodoHolobit,
)


def test_transpilador_asignacion():
    ast = [NodoAsignacion("x", 10)]
    t = TranspiladorASM()
    resultado = t.transpilar(ast)
    assert resultado == "SET x, 10"


def test_transpilador_condicional():
    ast = [
        NodoCondicional(
            "x > 5",
            [NodoAsignacion("y", 2)],
            [NodoAsignacion("y", 3)],
        )
    ]
    t = TranspiladorASM()
    resultado = t.transpilar(ast)
    expected = "IF x > 5\n    SET y, 2\nELSE\n    SET y, 3\nEND"
    assert resultado == expected


def test_transpilador_mientras():
    ast = [NodoBucleMientras("x > 0", [NodoAsignacion("x", "x - 1")])]
    t = TranspiladorASM()
    resultado = t.transpilar(ast)
    expected = "WHILE x > 0\n    SET x, x - 1\nEND"
    assert resultado == expected


def test_transpilador_funcion():
    ast = [NodoFuncion("miFuncion", ["a", "b"], [NodoAsignacion("x", "a + b")])]
    t = TranspiladorASM()
    resultado = t.transpilar(ast)
    expected = "FUNC miFuncion a b\n    SET x, a + b\nENDFUNC"
    assert resultado == expected


def test_transpilador_llamada_funcion():
    ast = [NodoLlamadaFuncion("miFuncion", ["a", "b"])]
    t = TranspiladorASM()
    resultado = t.transpilar(ast)
    assert resultado == "CALL miFuncion a, b"


def test_transpilador_holobit():
    ast = [NodoHolobit("miHolobit", [0.8, -0.5, 1.2])]
    t = TranspiladorASM()
    resultado = t.transpilar(ast)
    assert resultado == "HOLOBIT miHolobit [0.8, -0.5, 1.2]"
