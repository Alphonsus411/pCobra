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
    "js": ("pcobra.cobra.transpilers.transpiler.to_js", "TranspiladorJavaScript"),
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
        "holobit": ["from corelibs import *", "from standard_library import *", "holobit([1, 2, 3])"],
        "proyectar": ["proyectar(hb, '2d')"],
        "transformar": ["transformar(hb, 'rotar', 90)"],
        "graficar": ["graficar(hb)"],
        "corelibs": ["from corelibs import *", "longitud('cobra')"],
        "standard_library": ["from standard_library import *", "mostrar('hola')"],
    },
    "js": {
        "holobit": ["import * as io from './nativos/io.js';", "new Holobit([1, 2, 3])"],
        "proyectar": ["proyectar(hb, 2d);"],
        "transformar": ["transformar(hb, rotar, 90);"],
        "graficar": ["graficar(hb);"],
    },
}

PARTIAL_EXPECTATIONS = {
    "rust": {
        "holobit": ["holobit(vec![1, 2, 3]);"],
        "proyectar": ["fn cobra_proyectar", 'cobra_proyectar(&format!("{}", hb), &format!("{}", 2d));'],
        "transformar": ["fn cobra_transformar", 'cobra_transformar(&format!("{}", hb), &format!("{}", rotar), &[]);'],
        "graficar": ["fn cobra_graficar", 'cobra_graficar(&format!("{}", hb));'],
        "corelibs": ["longitud(cobra);"],
        "standard_library": ["mostrar(hola);"],
    },
    "wasm": {
        "holobit": [";; holobit hb [1, 2, 3]"],
        "proyectar": [";; runtime hook cobra_proyectar", ";; call runtime cobra_proyectar"],
        "transformar": [";; runtime hook cobra_transformar", ";; call runtime cobra_transformar"],
        "graficar": [";; runtime hook cobra_graficar", ";; call runtime cobra_graficar"],
        "corelibs": [";; call longitud (i32.const cobra)"],
        "standard_library": [";; call mostrar (i32.const hola)"],
    },
    "go": {
        "holobit": ["hb := []float64{1, 2, 3}"],
        "proyectar": ["func cobraProyectar", "cobraProyectar(hb, \"2d\")"],
        "transformar": ["func cobraTransformar", "cobraTransformar(hb, \"rotar\", 90)"],
        "graficar": ["func cobraGraficar", "cobraGraficar(hb)"],
        "corelibs": ["longitud(\"cobra\")"],
        "standard_library": ["mostrar(\"hola\")"],
    },
    "cpp": {
        "holobit": ["auto hb = holobit({ 1, 2, 3 });"],
        "proyectar": ["inline void cobra_proyectar", "cobra_proyectar(hb, 2d);"],
        "transformar": ["inline void cobra_transformar", "cobra_transformar(hb, rotar, {});"],
        "graficar": ["inline void cobra_graficar", "cobra_graficar(hb)"],
        "corelibs": ["longitud(cobra);"],
        "standard_library": ["mostrar(hola);"],
    },
    "java": {
        "holobit": ["double[] hb = new double[]{1, 2, 3};"],
        "proyectar": ["private static void cobraProyectar", "cobraProyectar(hb, \"2d\")"],
        "transformar": ["private static void cobraTransformar", "cobraTransformar(hb, \"rotar\", 90)"],
        "graficar": ["private static void cobraGraficar", "cobraGraficar(hb)"],
        "corelibs": ["longitud(\"cobra\")"],
        "standard_library": ["mostrar(\"hola\")"],
    },
    "asm": {
        "holobit": ["HOLOBIT hb [1, 2, 3]"],
        "proyectar": ["; hook cobra_proyectar", "; Nodo NodoProyectar no soportado"],
        "transformar": ["; hook cobra_transformar", "; Nodo NodoTransformar no soportado"],
        "graficar": ["; hook cobra_graficar", "; Nodo NodoGraficar no soportado"],
        "corelibs": ["CALL longitud 'cobra'"],
        "standard_library": ["CALL mostrar 'hola'"],
    },
    "js": {
        "corelibs": ["import * as texto from './nativos/texto.js';", "longitud(cobra);"],
        "standard_library": ["import * as io from './nativos/io.js';", "mostrar(hola);"],
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
    code = _generate(language, feature)
    for expected in FULL_EXPECTATIONS[language][feature]:
        assert expected in code


@pytest.mark.parametrize(
    "language, feature", [(lang, feat) for lang, feats in PARTIAL_EXPECTATIONS.items() for feat in feats]
)
def test_partial_compatibility_contract(language: str, feature: str):
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
