from cobra.transpilers.transpiler.to_cobol import TranspiladorCOBOL
from core.ast_nodes import (
    NodoAsignacion,
    NodoFuncion,
    NodoLlamadaFuncion,
    NodoImprimir,
    NodoValor,
    NodoRetorno,
)


HEADER = (
    "IDENTIFICATION DIVISION.\n"
    "PROGRAM-ID. MAIN.\n"
    "PROCEDURE DIVISION.\n"
)


def test_transpilador_asignacion_cobol():
    ast = [NodoAsignacion("X", 10)]
    t = TranspiladorCOBOL()
    resultado = t.generate_code(ast)
    esperado = HEADER + "    MOVE 10 TO X\n    STOP RUN."
    assert resultado == esperado


def test_transpilador_funcion_cobol():
    ast = [
        NodoFuncion("MIFUNCION", ["A", "B"], [NodoAsignacion("X", "A + B")])
    ]
    t = TranspiladorCOBOL()
    resultado = t.generate_code(ast)
    esperado = (
        HEADER
        + "    MIFUNCION SECTION.\n"
        + "        MOVE A + B TO X\n"
        + "    EXIT SECTION.\n"
        + "    STOP RUN."
    )
    assert resultado == esperado


def test_transpilador_llamada_funcion_cobol():
    ast = [NodoLlamadaFuncion("MIFUNCION", ["A", "B"])]
    t = TranspiladorCOBOL()
    resultado = t.generate_code(ast)
    esperado = HEADER + "    CALL 'MIFUNCION' USING A B\n    STOP RUN."
    assert resultado == esperado


def test_transpilador_imprimir_cobol():
    ast = [NodoImprimir(NodoValor("X"))]
    t = TranspiladorCOBOL()
    resultado = t.generate_code(ast)
    esperado = HEADER + "    DISPLAY X\n    STOP RUN."
    assert resultado == esperado


def test_transpilador_retorno_cobol():
    ast = [NodoFuncion("main", [], [NodoRetorno(NodoValor(1))])]
    t = TranspiladorCOBOL()
    resultado = t.generate_code(ast)
    esperado = (
        HEADER
        + "    main SECTION.\n"
        + "        DISPLAY 1\n"
        + "    EXIT SECTION.\n"
        + "    STOP RUN."
    )
    assert resultado == esperado

