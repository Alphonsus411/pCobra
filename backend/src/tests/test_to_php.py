from src.cobra.transpilers.transpiler.to_php import TranspiladorPHP
from src.core.ast_nodes import (
    NodoAsignacion,
    NodoFuncion,
    NodoLlamadaFuncion,
    NodoImprimir,
    NodoValor,
    NodoIdentificador,
)


def test_transpilador_asignacion_php():
    ast = [NodoAsignacion("x", 10)]
    t = TranspiladorPHP()
    resultado = t.transpilar(ast)
    assert resultado == "$x = 10;"


def test_transpilador_funcion_php():
    ast = [NodoFuncion("miFuncion", ["a", "b"], [NodoAsignacion("x", NodoIdentificador("a"))])]
    t = TranspiladorPHP()
    resultado = t.transpilar(ast)
    esperado = "function miFuncion($a, $b) {\n    $x = $a;\n}"
    assert resultado == esperado


def test_transpilador_llamada_funcion_php():
    ast = [NodoLlamadaFuncion("miFuncion", [NodoIdentificador("x"), NodoValor(3)])]
    t = TranspiladorPHP()
    resultado = t.transpilar(ast)
    assert resultado == "miFuncion($x, 3);"


def test_transpilador_imprimir_php():
    ast = [NodoImprimir(NodoIdentificador("x"))]
    t = TranspiladorPHP()
    resultado = t.transpilar(ast)
    assert resultado == "echo $x;"

