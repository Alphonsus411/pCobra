from src.cobra.transpilers.transpiler.to_cobol import TranspiladorCOBOL
from src.core.ast_nodes import NodoAsignacion, NodoFuncion, NodoLlamadaFuncion, NodoImprimir, NodoValor


def test_transpilador_asignacion_cobol():
    ast = [NodoAsignacion("X", 10)]
    t = TranspiladorCOBOL()
    resultado = t.transpilar(ast)
    assert resultado == "MOVE 10 TO X"


def test_transpilador_funcion_cobol():
    ast = [NodoFuncion("MIFUNCION", ["A", "B"], [NodoAsignacion("X", "A + B")])]
    t = TranspiladorCOBOL()
    resultado = t.transpilar(ast)
    esperado = "MIFUNCION SECTION.\n    MOVE A + B TO X\nEXIT SECTION."
    assert resultado == esperado


def test_transpilador_llamada_funcion_cobol():
    ast = [NodoLlamadaFuncion("MIFUNCION", ["A", "B"])]
    t = TranspiladorCOBOL()
    resultado = t.transpilar(ast)
    assert resultado == "CALL 'MIFUNCION' USING A B"


def test_transpilador_imprimir_cobol():
    ast = [NodoImprimir(NodoValor("X"))]
    t = TranspiladorCOBOL()
    resultado = t.transpilar(ast)
    assert resultado == "DISPLAY X"
