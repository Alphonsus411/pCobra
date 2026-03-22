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
    assert "cobra_proyectar(hb, '2d');" in code
    assert "cobra_transformar(hb, 'rotar', 90);" in code
    assert "cobra_graficar(hb);" in code



def test_js_runtime_snapshot_expone_adaptadores_corelibs_y_holobit():
    ast = [NodoHolobit("hb", [1, 2, 3])]
    code = TranspiladorJavaScript().generate_code(ast)
    assert "import * as interfaz from './nativos/interfaz.js';" in code
    assert "const longitud = (valor) => cobraJsCorelibs.longitud(valor);" in code
    assert "__cobra_tipo__: 'holobit'" in code
