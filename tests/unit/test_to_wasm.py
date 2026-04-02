from cobra.transpilers.transpiler.to_wasm import TranspiladorWasm
from core.ast_nodes import (
    NodoAsignacion,
    NodoFuncion,
    NodoOperacionBinaria,
    NodoIdentificador,
    NodoValor,
)
from cobra.core import Token, TipoToken


def test_transpilador_asignacion_wasm():
    ast = [NodoAsignacion("x", 10)]
    t = TranspiladorWasm()
    resultado = t.generate_code(ast)
    assert '(import "pcobra:corelibs" "longitud"' in resultado
    assert "(local.set $x (i32.const 10))" in resultado


def test_transpilador_funcion_wasm():
    expr = NodoOperacionBinaria(
        NodoIdentificador("a"),
        Token(TipoToken.SUMA, "+"),
        NodoIdentificador("b"),
    )
    ast = [NodoFuncion("sumar", ["a", "b"], [NodoAsignacion("x", expr)])]
    t = TranspiladorWasm()
    resultado = t.generate_code(ast)
    assert "(func $sumar (param $a i32) (param $b i32)" in resultado
    assert "(local.set $x (i32.add (local.get $a) (local.get $b)))" in resultado
