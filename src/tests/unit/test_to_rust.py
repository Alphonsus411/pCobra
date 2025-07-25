from cobra.transpilers.transpiler.to_rust import TranspiladorRust
from core.ast_nodes import (
    NodoAsignacion,
    NodoCondicional,
    NodoBucleMientras,
    NodoFuncion,
    NodoLlamadaFuncion,
    NodoHolobit,
    NodoClase,
    NodoMetodo,
    NodoYield,
    NodoValor,
    NodoTryCatch,
    NodoThrow,
    NodoIdentificador,
    NodoLista,
    NodoDiccionario,
    NodoAssert,
    NodoDel,
    NodoWith,
    NodoImportDesde,
    NodoOption,
    NodoSwitch,
    NodoCase,
    NodoGlobal,
    NodoNoLocal,
)


def test_transpilador_asignacion():
    ast = [NodoAsignacion("x", 10)]
    t = TranspiladorRust()
    resultado = t.generate_code(ast)
    assert resultado == "let x = 10;"


def test_transpilador_condicional():
    ast = [
        NodoCondicional(
            "x > 5",
            [NodoAsignacion("y", 2)],
            [NodoAsignacion("y", 3)],
        )
    ]
    t = TranspiladorRust()
    resultado = t.generate_code(ast)
    esperado = "if x > 5 {\n    let y = 2;\n} else {\n    let y = 3;\n}"
    assert resultado == esperado


def test_transpilador_mientras():
    ast = [NodoBucleMientras("x > 0", [NodoAsignacion("x", "x - 1")])]
    t = TranspiladorRust()
    resultado = t.generate_code(ast)
    esperado = "while x > 0 {\n    let x = x - 1;\n}"
    assert resultado == esperado


def test_transpilador_funcion():
    ast = [NodoFuncion("miFuncion", ["a", "b"], [NodoAsignacion("x", "a + b")])]
    t = TranspiladorRust()
    resultado = t.generate_code(ast)
    esperado = "fn miFuncion(a, b) {\n    let x = a + b;\n}"
    assert resultado == esperado


def test_transpilador_llamada_funcion():
    ast = [NodoLlamadaFuncion("miFuncion", ["a", "b"])]
    t = TranspiladorRust()
    resultado = t.generate_code(ast)
    assert resultado == "miFuncion(a, b);"


def test_transpilador_holobit():
    ast = [NodoHolobit("miHolobit", [0.8, -0.5, 1.2])]
    t = TranspiladorRust()
    resultado = t.generate_code(ast)
    assert resultado == "let miHolobit = holobit(vec![0.8, -0.5, 1.2]);"

def test_transpilador_clase():
    metodo = NodoMetodo("saludar", ["self"], [NodoAsignacion("x", 1)])
    ast = [NodoClase("Persona", [metodo])]
    t = TranspiladorRust()
    resultado = t.generate_code(ast)
    esperado = (
        "struct Persona {}\n\n"
        "impl Persona {\n"
        "    fn saludar(self) {\n"
        "        let x = 1;\n"
        "    }\n"
        "}"
    )
    assert resultado == esperado


def test_transpilador_yield():
    ast = [NodoFuncion("generador", [], [NodoYield(NodoValor(1))])]
    t = TranspiladorRust()
    resultado = t.generate_code(ast)
    esperado = "fn generador() {\n    yield 1;\n}"
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
    t = TranspiladorRust()
    resultado = t.generate_code(ast)
    esperado = (
        "match x {\n"
        "    1 => {\n"
        "        let y = 1;\n"
        "    },\n"
        "    2 => {\n"
        "        let y = 2;\n"
        "    },\n"
        "    _ => {\n"
        "        let y = 0;\n"
        "    },\n"
        "}"
    )
    assert resultado == esperado

def test_try_catch_result():
    nodo = NodoTryCatch(
        [NodoThrow(NodoValor("1"))],
        "e",
        [NodoAsignacion("y", NodoIdentificador("e"))],
    )
    t = TranspiladorRust()
    resultado = t.generate_code([nodo])
    esperado = (
        "let resultado: Result<(), Box<dyn std::error::Error>> = (|| {\n"
        "    return Err(1.into());\n"
        "    Ok(())\n"
        "})();\n"
        "match resultado {\n"
        "    Ok(_) => (),\n"
        "    Err(e) => {\n"
        "        let e = e;\n"
        "        let y = e;\n"
        "    },\n"
        "};"
    )
    assert resultado == esperado


def test_option_some_none():
    ast = [
        NodoAsignacion("a", NodoOption(NodoValor(5))),
        NodoAsignacion("b", NodoOption(None)),
    ]
    t = TranspiladorRust()
    resultado = t.generate_code(ast)
    esperado = "let a = Some(5);\nlet b = None;"
    assert resultado == esperado


def test_option_match():
    ast = [
        NodoAsignacion("opt", NodoOption(NodoValor(1))),
        NodoSwitch(
            NodoIdentificador("opt"),
            [
                NodoCase(
                    NodoOption(NodoIdentificador("v")),
                    [NodoAsignacion("y", NodoIdentificador("v"))],
                ),
                NodoCase(NodoOption(None), [NodoAsignacion("y", NodoValor(0))]),
            ],
            [],
        ),
    ]
    t = TranspiladorRust()
    resultado = t.generate_code(ast)
    esperado = (
        "let opt = Some(1);\n"
        "match opt {\n"
        "    Some(v) => {\n"
        "        let y = v;\n"
        "    },\n"
        "    None => {\n"
        "        let y = 0;\n"
        "    },\n"
        "}"
    )
    assert resultado == esperado


def test_transpilador_assert_del_with_import():
    ast = [
        NodoAssert(NodoValor(True)),
        NodoDel(NodoIdentificador("x")),
        NodoWith(None, None, [NodoAsignacion("y", NodoValor(1))]),
        NodoImportDesde("mod", "func"),
    ]
    t = TranspiladorRust()
    resultado = t.generate_code(ast)
    esperado = (
        "assert!(True);\n"
        "// del x\n"
        "{\n"
        "    let y = 1;\n"
        "}\n"
        "use mod::func;"
    )
    assert resultado == esperado


def test_obtener_valor_listas_diccionarios():
    ast = [
        NodoAsignacion("a", NodoLista([NodoValor(1), NodoValor(2)])),
        NodoAsignacion(
            "b",
            NodoDiccionario([(NodoValor("x"), NodoValor(1))]),
        ),
    ]
    t = TranspiladorRust()
    resultado = t.generate_code(ast)
    esperado = (
        "let a = vec![1, 2];\n"
        "let b = std::collections::HashMap::from([(x, 1)]);"
    )
    assert resultado == esperado


def test_transpilador_global_rust():
    ast = [NodoGlobal(["a", "b"])]
    t = TranspiladorRust()
    resultado = t.generate_code(ast)
    assert resultado == "// global a, b"


def test_transpilador_nolocal_rust():
    ast = [NodoNoLocal(["x"])]
    t = TranspiladorRust()
    resultado = t.generate_code(ast)
    assert resultado == "// nonlocal x"

