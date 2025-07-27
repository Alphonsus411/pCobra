import pytest
from cobra.transpilers.transpiler.to_js import TranspiladorJavaScript
from cobra.transpilers.import_helper import get_standard_imports
from core.ast_nodes import (
    NodoAsignacion,
    NodoCondicional,
    NodoBucleMientras,
    NodoFuncion,
    NodoLlamadaFuncion,
    NodoHolobit,
    NodoYield,
    NodoEsperar,
    NodoValor,
    NodoDecorador,
    NodoIdentificador,
    NodoMetodo,
    NodoClase,
    NodoPasar,
    NodoSwitch,
    NodoCase,
    NodoGlobal,
    NodoNoLocal,
    NodoImportDesde,
    NodoExport,
)

IMPORTS = "".join(f"{line}\n" for line in get_standard_imports("js"))


def test_transpilador_asignacion():
    ast = [NodoAsignacion("x", 10)]
    transpilador = TranspiladorJavaScript()
    resultado = transpilador.generate_code(ast)
    assert resultado == IMPORTS + "let x = 10;"


def test_transpilador_condicional():
    ast = [NodoCondicional("x > 5", [NodoAsignacion("y", 2)], [NodoAsignacion("y", 3)])]
    transpilador = TranspiladorJavaScript()
    resultado = transpilador.generate_code(ast)
    expected = (
        IMPORTS
        + "if (x > 5) {\n    let y = 2;\n} else {\n    let y = 3;\n}"
    )
    assert resultado == expected


def test_transpilador_mientras():
    ast = [NodoBucleMientras("x > 0", [NodoAsignacion("x", "x - 1")])]
    transpilador = TranspiladorJavaScript()
    resultado = transpilador.generate_code(ast)
    expected = IMPORTS + "while (x > 0) {\n    let x = x - 1;\n}"
    assert resultado == expected


def test_transpilador_funcion():
    ast = [NodoFuncion("miFuncion", ["a", "b"], [NodoAsignacion("x", "a + b")])]
    transpilador = TranspiladorJavaScript()
    resultado = transpilador.generate_code(ast)
    expected = IMPORTS + "function miFuncion(a, b) {\n    let x = a + b;\n}"
    assert resultado == expected


def test_transpilador_llamada_funcion():
    ast = [NodoLlamadaFuncion("miFuncion", ["a", "b"])]
    transpilador = TranspiladorJavaScript()
    resultado = transpilador.generate_code(ast)
    expected = IMPORTS + "miFuncion(a, b);"
    assert resultado == expected


def test_transpilador_holobit():
    ast = [NodoHolobit("miHolobit", [0.8, -0.5, 1.2])]
    transpilador = TranspiladorJavaScript()
    resultado = transpilador.generate_code(ast)
    expected = IMPORTS + "let miHolobit = new Holobit([0.8, -0.5, 1.2]);"
    assert resultado == expected


def test_transpilador_yield():
    ast = [NodoFuncion("generador", [], [NodoYield(NodoValor(1))])]
    t = TranspiladorJavaScript()
    resultado = t.generate_code(ast)
    esperado = IMPORTS + "function generador() {\nyield 1;\n}"
    assert resultado == esperado


def test_transpilador_decoradores_funcion_js():
    d1 = NodoDecorador(NodoIdentificador("d1"))
    d2 = NodoDecorador(NodoIdentificador("d2"))
    func = NodoFuncion("saluda", [], [NodoPasar()], [d1, d2])
    t = TranspiladorJavaScript()
    resultado = t.generate_code([func])
    esperado = IMPORTS + (
        "function saluda() {\n"
        + ";\n"
        + "}\n"
        + "saluda = d2(saluda);\n"
        + "saluda = d1(saluda);"
    )
    assert resultado == esperado


def test_transpilador_switch():
    ast = [
        NodoSwitch(
            "x",
            [
                NodoCase(NodoValor(1), [NodoAsignacion("y", NodoValor(1))]),
                NodoCase(NodoValor(2), [NodoAsignacion("y", NodoValor(2))]),
            ],
            [NodoAsignacion("y", NodoValor(0))],
        )
    ]
    t = TranspiladorJavaScript()
    resultado = t.generate_code(ast)
    esperado = (
        IMPORTS
        + "switch (x) {\n"
        + "    case 1:\n"
        + "        let y = 1;\n"
        + "        break;\n"
        + "    case 2:\n"
        + "        let y = 2;\n"
        + "        break;\n"
        + "    default:\n"
        + "        let y = 0;\n"
        + "        break;\n"
        + "}"
    )
    assert resultado == esperado


def test_async_function_and_await():
    ast = [
        NodoFuncion(
            "principal",
            [],
            [NodoEsperar(NodoLlamadaFuncion("saluda", []))],
            asincronica=True,
        )
    ]
    t = TranspiladorJavaScript()
    resultado = t.generate_code(ast)
    esperado = IMPORTS + (
        "async function principal() {\n"
        + "await saluda();\n"
        + "}"
    )
    assert resultado == esperado


def test_export_import():
    ast = [
        NodoImportDesde("./mod.js", "saluda"),
        NodoFuncion("saluda", [], []),
        NodoExport("saluda"),
    ]
    t = TranspiladorJavaScript()
    resultado = t.generate_code(ast)
    esperado = IMPORTS + (
        "import { saluda } from './mod.js';\n"
        + "function saluda() {\n"
        + "}\n"
        + "export { saluda };"
    )
    assert resultado == esperado

def test_decoradores_en_clase_y_metodo_js():
    decor = NodoDecorador(NodoIdentificador("dec"))
    metodo = NodoMetodo("run", ["a"], [NodoPasar()], asincronica=True)
    metodo.decoradores = [decor]
    clase = NodoClase("C", [metodo])
    clase.decoradores = [decor]
    t = TranspiladorJavaScript()
    resultado = t.generate_code([clase])
    esperado = IMPORTS + (
        "class C {\n"
        + "async run(a) {\n"
        + ";\n"
        + "}\n"
        + "}\n"
        + "C.prototype.run = dec(C.prototype.run);\n"
        + "C = dec(C);"
    )
    assert resultado == esperado


def test_imports_js_por_defecto():
    resultado = TranspiladorJavaScript().generate_code([])
    esperado = "\n".join(get_standard_imports("js"))
    assert resultado == esperado


def test_transpilador_global_js():
    ast = [NodoGlobal(["a", "b"])]
    t = TranspiladorJavaScript()
    resultado = t.generate_code(ast)
    assert resultado == IMPORTS + "// global a, b"


def test_transpilador_nolocal_js():
    ast = [NodoNoLocal(["x"])]
    t = TranspiladorJavaScript()
    resultado = t.generate_code(ast)
    assert resultado == IMPORTS + "// nonlocal x"
