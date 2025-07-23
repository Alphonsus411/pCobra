from cobra.transpilers.transpiler.to_perl import TranspiladorPerl
from core.ast_nodes import NodoAsignacion, NodoFuncion, NodoValor, NodoIdentificador


def test_transpilador_asignacion_perl():
    ast = [NodoAsignacion("x", 10)]
    t = TranspiladorPerl()
    resultado = t.generate_code(ast)
    assert resultado == "$x = 10;"


def test_transpilador_funcion_perl():
    ast = [NodoFuncion("miFuncion", ["a", "b"], [NodoAsignacion("x", NodoIdentificador("a"))])]
    t = TranspiladorPerl()
    resultado = t.generate_code(ast)
    esperado = "sub miFuncion {\n    my ($a, $b) = @_;\n    $x = $a;\n}"
    assert resultado == esperado
