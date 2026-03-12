from pcobra.core.ast_nodes import (
    NodoGraficar,
    NodoHolobit,
    NodoIdentificador,
    NodoProyectar,
    NodoTransformar,
    NodoValor,
)
from pcobra.cobra.transpilers.transpiler.to_js import TranspiladorJavaScript


def test_js_codegen_holobit_runtime_hooks_snapshot():
    ast = [
        NodoHolobit("hb", [1, 2, 3]),
        NodoProyectar(NodoIdentificador("hb"), NodoValor("2d")),
        NodoTransformar(NodoIdentificador("hb"), NodoValor("rotar"), [NodoValor(90)]),
        NodoGraficar(NodoIdentificador("hb")),
    ]

    code = TranspiladorJavaScript().generate_code(ast)

    assert "function cobra_proyectar(hb, modo) {" in code
    assert "function cobra_transformar(hb, op, ...params) {" in code
    assert "function cobra_graficar(hb) {" in code
    assert "cobra_proyectar(hb, 2d);" in code
    assert "cobra_transformar(hb, rotar, 90);" in code
    assert "cobra_graficar(hb);" in code
