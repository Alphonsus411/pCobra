"""Contratos de regresión para los 8 backends oficiales por tier."""

from __future__ import annotations

import importlib

from pcobra.core.ast_nodes import (
    NodoGraficar,
    NodoHolobit,
    NodoIdentificador,
    NodoLlamadaFuncion,
    NodoProyectar,
    NodoTransformar,
    NodoValor,
)

TRANSPILERS: dict[str, tuple[str, str]] = {
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

STRICT_FULL_EXPECTATIONS: dict[str, dict[str, tuple[str, ...]]] = {
    "python": {
        "holobit": (
            "from corelibs import *",
            "from standard_library import *",
            "hb = holobit([1, 2, 3])",
        ),
        "proyectar": ("proyectar(hb, '2d')",),
        "transformar": ("transformar(hb, 'rotar', 90)",),
        "graficar": ("graficar(hb)",),
        "corelibs": ("longitud('cobra')",),
        "standard_library": ("mostrar('hola')",),
    },
    "js": {
        "holobit": (
            "import * as io from './nativos/io.js';",
            "import * as texto from './nativos/texto.js';",
            "let hb = new Holobit([1, 2, 3]);",
        ),
        "proyectar": ("proyectar(hb, 2d);",),
        "transformar": ("transformar(hb, rotar, 90);",),
        "graficar": ("graficar(hb);",),
    },
}

PARTIAL_EXPECTATIONS: dict[str, dict[str, tuple[str, ...]]] = {
    "js": {
        "corelibs": ("longitud(cobra);",),
        "standard_library": ("mostrar(hola);",),
    },
    "rust": {
        "holobit": ("let hb = holobit(vec![1, 2, 3]);",),
        "proyectar": ("fn cobra_proyectar", "cobra_proyectar(&format!(\"{}\", hb), &format!(\"{}\", 2d));"),
        "transformar": (
            "fn cobra_transformar",
            "cobra_transformar(&format!(\"{}\", hb), &format!(\"{}\", rotar), &[]);",
        ),
        "graficar": ("fn cobra_graficar", "cobra_graficar(&format!(\"{}\", hb));"),
        "corelibs": ("longitud(cobra);",),
        "standard_library": ("mostrar(hola);",),
    },
    "wasm": {
        "holobit": (";; holobit hb [1, 2, 3]",),
        "proyectar": (";; runtime hook cobra_proyectar", ";; call runtime cobra_proyectar"),
        "transformar": (";; runtime hook cobra_transformar", ";; call runtime cobra_transformar"),
        "graficar": (";; runtime hook cobra_graficar", ";; call runtime cobra_graficar"),
        "corelibs": (";; call longitud (i32.const cobra)",),
        "standard_library": (";; call mostrar (i32.const hola)",),
    },
    "go": {
        "holobit": ("hb := []float64{1, 2, 3}",),
        "proyectar": ("func cobraProyectar", 'cobraProyectar(hb, "2d")'),
        "transformar": ("func cobraTransformar", 'cobraTransformar(hb, "rotar", 90)'),
        "graficar": ("func cobraGraficar", "cobraGraficar(hb)"),
        "corelibs": ('longitud("cobra")',),
        "standard_library": ('mostrar("hola")',),
    },
    "cpp": {
        "holobit": ("auto hb = holobit({ 1, 2, 3 });",),
        "proyectar": ("inline void cobra_proyectar", "cobra_proyectar(hb, 2d);"),
        "transformar": ("inline void cobra_transformar", "cobra_transformar(hb, rotar, {});"),
        "graficar": ("inline void cobra_graficar", "cobra_graficar(hb);"),
        "corelibs": ("longitud(cobra);",),
        "standard_library": ("mostrar(hola);",),
    },
    "java": {
        "holobit": ("double[] hb = new double[]{1, 2, 3};",),
        "proyectar": ("private static void cobraProyectar", 'cobraProyectar(hb, "2d")'),
        "transformar": ("private static void cobraTransformar", 'cobraTransformar(hb, "rotar", 90)'),
        "graficar": ("private static void cobraGraficar", "cobraGraficar(hb);"),
        "corelibs": ('longitud("cobra")',),
        "standard_library": ('mostrar("hola")',),
    },
    "asm": {
        "holobit": ("HOLOBIT hb [1, 2, 3]",),
        "proyectar": ("; hook cobra_proyectar", "; Nodo NodoProyectar no soportado"),
        "transformar": ("; hook cobra_transformar", "; Nodo NodoTransformar no soportado"),
        "graficar": ("; hook cobra_graficar", "; Nodo NodoGraficar no soportado"),
        "corelibs": ("CALL longitud 'cobra'",),
        "standard_library": ("CALL mostrar 'hola'",),
    },
}


def generate_code(language: str, feature: str) -> str:
    module_name, class_name = TRANSPILERS[language]
    transpiler_class = getattr(importlib.import_module(module_name), class_name)
    output = transpiler_class().generate_code(FEATURE_NODES[feature]())
    return "\n".join(output) if isinstance(output, list) else str(output)
