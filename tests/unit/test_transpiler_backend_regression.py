import importlib

import pytest

from pcobra.core.ast_nodes import (
    NodoGraficar,
    NodoHolobit,
    NodoIdentificador,
    NodoLlamadaFuncion,
    NodoProyectar,
    NodoTransformar,
    NodoValor,
)
from pcobra.cobra.transpilers.compatibility_matrix import BACKEND_COMPATIBILITY
from pcobra.cobra.transpilers.targets import TIER1_TARGETS, TIER2_TARGETS

TRANSPILERS = {
    "python": ("pcobra.cobra.transpilers.transpiler.to_python", "TranspiladorPython"),
    "javascript": ("pcobra.cobra.transpilers.transpiler.to_js", "TranspiladorJavaScript"),
    "rust": ("pcobra.cobra.transpilers.transpiler.to_rust", "TranspiladorRust"),
    "wasm": ("pcobra.cobra.transpilers.transpiler.to_wasm", "TranspiladorWasm"),
    "go": ("pcobra.cobra.transpilers.transpiler.to_go", "TranspiladorGo"),
    "cpp": ("pcobra.cobra.transpilers.transpiler.to_cpp", "TranspiladorCPP"),
    "java": ("pcobra.cobra.transpilers.transpiler.to_java", "TranspiladorJava"),
    "asm": ("pcobra.cobra.transpilers.transpiler.to_asm", "TranspiladorASM"),
}

FEATURE_NODES = {
    "holobit": lambda: [NodoHolobit("hb", [1, 2, 3])],
    "proyectar": lambda: [NodoHolobit("hb", [1, 2, 3]), NodoProyectar(NodoIdentificador("hb"), NodoValor("2d"))],
    "transformar": lambda: [NodoHolobit("hb", [1, 2, 3]), NodoTransformar(NodoIdentificador("hb"), NodoValor("rotar"), [NodoValor(90)])],
    "graficar": lambda: [NodoHolobit("hb", [1, 2, 3]), NodoGraficar(NodoIdentificador("hb"))],
    "corelibs": lambda: [NodoLlamadaFuncion("longitud", [NodoValor("cobra")])],
    "standard_library": lambda: [NodoLlamadaFuncion("mostrar", [NodoValor("hola")])],
}

FULL_EXPECTATIONS = {
    "python": {
        "holobit": ["import pcobra.corelibs as _pcobra_corelibs", "import pcobra.standard_library as _pcobra_standard_library", "hb = cobra_holobit([1, 2, 3])"],
        "proyectar": ["def cobra_proyectar", "cobra_proyectar(hb, '2d')"],
        "transformar": ["def cobra_transformar", "cobra_transformar(hb, 'rotar', 90)"],
        "graficar": ["def cobra_graficar", "cobra_graficar(hb)"],
        "corelibs": ["import pcobra.corelibs as _pcobra_corelibs", "longitud('cobra')"],
        "standard_library": ["import pcobra.standard_library as _pcobra_standard_library", "mostrar('hola')"],
    },
}

PARTIAL_EXPECTATIONS = {
    "javascript": {
        "holobit": ["function cobra_holobit", "let hb = cobra_holobit([1, 2, 3]);", "__cobra_tipo__: 'holobit'"],
        "proyectar": ["function cobra_proyectar", "case '2d':", "cobra_proyectar(hb, '2d');"],
        "transformar": ["function cobra_transformar", "operacion === 'rotar'", "cobra_transformar(hb, 'rotar', 90);"],
        "graficar": ["function cobra_graficar", "const vista = `Holobit(${holobit.valores.join(', ')})`;", "cobra_graficar(hb);"],
        "corelibs": ["import * as interfaz from './nativos/interfaz.js';", "longitud('cobra');"],
        "standard_library": ["const mostrar = (...args) => cobraJsStandardLibrary.mostrar(...args);", "mostrar('hola');"],
    },
    "rust": {
        "holobit": ["struct CobraHolobit", "let hb = cobra_holobit(vec![1, 2, 3]);"],
        "proyectar": ["fn cobra_proyectar", 'let _ = cobra_proyectar(&hb, &format!("{}", "2d"));'],
        "transformar": ["fn cobra_transformar", 'let _ = cobra_transformar(&hb, &format!("{}", "rotar"), &[90 as f64]);'],
        "graficar": ["fn cobra_graficar", 'let _ = cobra_graficar(&hb);'],
        "corelibs": ['fn longitud<T: ToString>(valor: T) -> usize {', 'longitud("cobra");'],
        "standard_library": ['fn mostrar<T: Display>(valor: T) {', 'mostrar("hola");'],
    },
    "wasm": {
        "holobit": ['(import "pcobra:holobit" "cobra_holobit"', "(drop (call $cobra_holobit (i32.const 1)))"],
        "proyectar": ["(func $cobra_proyectar", "(drop (call $cobra_proyectar (local.get $hb) (i32.const 0)))"],
        "transformar": ["(func $cobra_transformar", "(drop (call $cobra_transformar (local.get $hb) (i32.const 0) (i32.const 1)))"],
        "graficar": ["(func $cobra_graficar", "(drop (call $cobra_graficar (local.get $hb)))"],
        "corelibs": ['(import "pcobra:corelibs" "longitud"', "(call $longitud (i32.const 0))"],
        "standard_library": ['(import "pcobra:standard_library" "mostrar"', "(call $mostrar (i32.const 0))"],
    },
    "go": {
        "holobit": ["hb := cobra_holobit([]float64{1, 2, 3})"],
        "proyectar": ["func cobra_proyectar", 'cobra_proyectar(hb, "2d")'],
        "transformar": ["func cobra_transformar", 'cobra_transformar(hb, "rotar", 90)'],
        "graficar": ["func cobra_graficar", "cobra_graficar(hb)"],
        "corelibs": ['longitud("cobra")'],
        "standard_library": ['mostrar("hola")'],
    },
    "cpp": {
        "holobit": ["auto hb = cobra_holobit({ 1, 2, 3 });"],
        "proyectar": ["inline void cobra_proyectar", 'cobra_proyectar(hb, "2d");'],
        "transformar": ["inline void cobra_transformar", 'cobra_transformar(hb, "rotar", {});'],
        "graficar": ["inline void cobra_graficar", "cobra_graficar(hb);"],
        "corelibs": ['longitud("cobra");'],
        "standard_library": ['mostrar("hola");'],
    },
    "java": {
        "holobit": ["Object hb = cobra_holobit(new double[]{1, 2, 3});"],
        "proyectar": ["private static void cobra_proyectar", 'cobra_proyectar(hb, "2d")'],
        "transformar": ["private static void cobra_transformar", 'cobra_transformar(hb, "rotar", 90)'],
        "graficar": ["private static void cobra_graficar", "cobra_graficar(hb);"],
        "corelibs": ['longitud("cobra")'],
        "standard_library": ['mostrar("hola")'],
    },
    "asm": {
        "holobit": ["HOLOBIT hb [1, 2, 3]"],
        "proyectar": ["cobra_proyectar:", "CALL cobra_proyectar hb, '2d'"],
        "transformar": ["cobra_transformar:", "CALL cobra_transformar hb, 'rotar', 90"],
        "graficar": ["cobra_graficar:", "CALL cobra_graficar hb"],
        "corelibs": ["CALL longitud 'cobra'"],
        "standard_library": ["CALL mostrar 'hola'"],
    },
}


def _build(language: str):
    mod_name, cls_name = TRANSPILERS[language]
    mod = importlib.import_module(mod_name)
    return getattr(mod, cls_name)()


def _to_text(output) -> str:
    return "\n".join(output) if isinstance(output, list) else str(output)


def _generate(language: str, feature: str) -> str:
    transpiler = _build(language)
    return _to_text(transpiler.generate_code(FEATURE_NODES[feature]()))


@pytest.mark.parametrize("language", TIER1_TARGETS)
def test_tier1_backends_import_and_generate(language: str):
    code = _generate(language, "holobit")
    assert code.strip()


@pytest.mark.parametrize("language", TIER2_TARGETS)
def test_tier2_backends_import_and_generate(language: str):
    code = _generate(language, "holobit")
    assert code.strip()


@pytest.mark.parametrize("language, feature", [(lang, feat) for lang, feats in FULL_EXPECTATIONS.items() for feat in feats])
def test_full_compatibility_contract(language: str, feature: str):
    assert BACKEND_COMPATIBILITY[language][feature] == "full"
    code = _generate(language, feature)
    for expected in FULL_EXPECTATIONS[language][feature]:
        assert expected in code


@pytest.mark.parametrize("language, feature", [(lang, feat) for lang, feats in PARTIAL_EXPECTATIONS.items() for feat in feats])
def test_partial_compatibility_contract(language: str, feature: str):
    assert BACKEND_COMPATIBILITY[language][feature] == "partial"
    code = _generate(language, feature)
    for expected in PARTIAL_EXPECTATIONS[language][feature]:
        assert expected in code


@pytest.mark.parametrize("language", TRANSPILERS)
def test_suite_covers_all_features(language: str):
    for feature in FEATURE_NODES:
        code = _generate(language, feature)
        assert code.strip()


def test_matriz_compatibilidad_cubre_todos_los_backends_oficiales():
    assert set(BACKEND_COMPATIBILITY) == set(TRANSPILERS)
