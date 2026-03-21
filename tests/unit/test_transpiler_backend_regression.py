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
    "proyectar": lambda: [
        NodoHolobit("hb", [1, 2, 3]),
        NodoProyectar(NodoIdentificador("hb"), NodoValor("2d")),
    ],
    "transformar": lambda: [
        NodoHolobit("hb", [1, 2, 3]),
        NodoTransformar(NodoIdentificador("hb"), NodoValor("rotar"), [NodoValor(90)]),
    ],
    "graficar": lambda: [NodoHolobit("hb", [1, 2, 3]), NodoGraficar(NodoIdentificador("hb"))],
    "corelibs": lambda: [NodoLlamadaFuncion("longitud", [NodoValor("cobra")])],
    "standard_library": lambda: [NodoLlamadaFuncion("mostrar", [NodoValor("hola")])],
}

FULL_EXPECTATIONS = {
    "python": {
        "holobit": ["from corelibs import *", "from standard_library import *", "hb = cobra_holobit([1, 2, 3])"],
        "proyectar": ["def cobra_proyectar", "cobra_proyectar(hb, '2d')"],
        "transformar": ["def cobra_transformar", "cobra_transformar(hb, 'rotar', 90)"],
        "graficar": ["def cobra_graficar", "cobra_graficar(hb)"],
        "corelibs": ["from corelibs import *", "longitud('cobra')"],
        "standard_library": ["from standard_library import *", "mostrar('hola')"],
    },
}

PARTIAL_EXPECTATIONS = {
    "javascript": {
        "holobit": ["function cobra_holobit", "let hb = cobra_holobit([1, 2, 3]);"],
        "proyectar": ["function cobra_proyectar", "Runtime Holobit JavaScript: 'proyectar' requiere runtime avanzado compatible.", "cobra_proyectar(hb, '2d');"],
        "transformar": ["function cobra_transformar", "Runtime Holobit JavaScript: 'transformar' requiere runtime avanzado compatible.", "cobra_transformar(hb, 'rotar', 90);"],
        "graficar": ["function cobra_graficar", "Runtime Holobit JavaScript: 'graficar' requiere runtime avanzado compatible.", "cobra_graficar(hb);"],
        "corelibs": ["import * as texto from './nativos/texto.js';", "longitud('cobra');"],
        "standard_library": ["import * as io from './nativos/io.js';", "mostrar('hola');"],
    },
    "rust": {
        "holobit": ["let hb = cobra_holobit(vec![1, 2, 3]);"],
        "proyectar": ["fn cobra_proyectar", 'cobra_proyectar(&format!("{}", hb), &format!("{}", "2d"));'],
        "transformar": ["fn cobra_transformar", 'cobra_transformar(&format!("{}", hb), &format!("{}", "rotar"), &[]);'],
        "graficar": ["fn cobra_graficar", 'cobra_graficar(&format!("{}", hb));'],
        "corelibs": ['longitud("cobra");'],
        "standard_library": ['mostrar("hola");'],
    },
    "wasm": {
        "holobit": ["(drop (call $cobra_holobit (i32.const 1)))"],
        "proyectar": ["(func $cobra_proyectar", "(call $cobra_proyectar (local.get $hb) (i32.const 0))"],
        "transformar": ["(func $cobra_transformar", "(call $cobra_transformar (local.get $hb) (i32.const 0))"],
        "graficar": ["(func $cobra_graficar", "(call $cobra_graficar (local.get $hb))"],
        "corelibs": ["(call $longitud (i32.const 0))"],
        "standard_library": ["(call $mostrar (i32.const 0))"],
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


@pytest.mark.parametrize(
    "language, feature", [(lang, feat) for lang, feats in PARTIAL_EXPECTATIONS.items() for feat in feats]
)
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
