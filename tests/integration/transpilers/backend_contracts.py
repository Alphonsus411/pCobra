"""Contratos de regresión para los 8 backends oficiales por tier."""

from __future__ import annotations

import importlib
from typing import Final

from pcobra.core.ast_nodes import (
    NodoGraficar,
    NodoHolobit,
    NodoIdentificador,
    NodoLlamadaFuncion,
    NodoProyectar,
    NodoTransformar,
    NodoValor,
)

REQUIRED_FEATURES: Final[tuple[str, ...]] = (
    "holobit",
    "proyectar",
    "transformar",
    "graficar",
    "corelibs",
    "standard_library",
)

HOLOBIT_FEATURES: Final[tuple[str, ...]] = (
    "holobit",
    "proyectar",
    "transformar",
    "graficar",
)

CORE_RUNTIME_FEATURES: Final[tuple[str, ...]] = (
    "corelibs",
    "standard_library",
)

TRANSPILERS: dict[str, tuple[str, str]] = {
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

STRICT_FULL_EXPECTATIONS: dict[str, dict[str, tuple[str, ...]]] = {
    "python": {
        "holobit": (
            "import pcobra.corelibs as _pcobra_corelibs",
            "import pcobra.standard_library as _pcobra_standard_library",
            "hb = cobra_holobit([1, 2, 3])",
        ),
        "proyectar": ("def cobra_proyectar", "cobra_proyectar(hb, '2d')"),
        "transformar": ("def cobra_transformar", "cobra_transformar(hb, 'rotar', 90)"),
        "graficar": ("def cobra_graficar", "cobra_graficar(hb)"),
        "corelibs": ("longitud('cobra')",),
        "standard_library": ("mostrar('hola')",),
    },
}

PARTIAL_EXPECTATIONS: dict[str, dict[str, tuple[str, ...]]] = {
    "javascript": {
        "holobit": (
            "function cobra_holobit",
            "let hb = cobra_holobit([1, 2, 3]);",
            "__cobra_tipo__: 'holobit'",
        ),
        "proyectar": ("function cobra_proyectar", "case '2d':", "cobra_proyectar(hb, '2d');"),
        "transformar": (
            "function cobra_transformar",
            "operacion === 'rotar'",
            "cobra_transformar(hb, 'rotar', 90);",
        ),
        "graficar": (
            "function cobra_graficar",
            "const vista = `Holobit(${holobit.valores.join(', ')})`;",
            "cobra_graficar(hb);",
        ),
        "corelibs": (
            "const longitud = (valor) => cobraJsCorelibs.longitud(valor);",
            "longitud('cobra');",
        ),
        "standard_library": (
            "const mostrar = (...args) => cobraJsStandardLibrary.mostrar(...args);",
            "mostrar('hola');",
        ),
    },
    "rust": {
        "holobit": ("struct CobraHolobit", "let hb = cobra_holobit(vec![1, 2, 3]);"),
        "proyectar": (
            "fn cobra_proyectar",
            'cobra_runtime_expect(cobra_proyectar(&hb, &format!("{}", "2d")));',
        ),
        "transformar": (
            "fn cobra_transformar",
            'cobra_runtime_expect(cobra_transformar(&hb, &format!("{}", "rotar"), &[format!("{}", 90)]));',
        ),
        "graficar": ("fn cobra_graficar", 'cobra_runtime_expect(cobra_graficar(&hb));'),
        "corelibs": ('fn longitud<T: ToString>(valor: T) -> usize {', 'longitud("cobra");'),
        "standard_library": ('fn mostrar<T: Display>(valor: T) {', 'mostrar("hola");'),
    },
    "wasm": {
        "holobit": (
            '(import "pcobra:holobit" "cobra_holobit"',
            '(drop (call $cobra_holobit (i32.const 1)))',
        ),
        "proyectar": (
            "(func $cobra_proyectar",
            "(drop (call $cobra_proyectar (local.get $hb) (i32.const 0)))",
        ),
        "transformar": (
            "(func $cobra_transformar",
            "(drop (call $cobra_transformar (local.get $hb) (i32.const 0) (i32.const 1)))",
        ),
        "graficar": (
            "(func $cobra_graficar",
            "(drop (call $cobra_graficar (local.get $hb)))",
        ),
        "corelibs": ('(import "pcobra:corelibs" "longitud"', '(call $longitud (i32.const 0))'),
        "standard_library": (
            '(import "pcobra:standard_library" "mostrar"',
            '(call $mostrar (i32.const 0))',
        ),
    },
    "go": {
        "holobit": ("hb := cobra_holobit([]float64{1, 2, 3})",),
        "proyectar": ("func cobra_proyectar", 'cobra_proyectar(hb, "2d")'),
        "transformar": ("func cobra_transformar", 'cobra_transformar(hb, "rotar", 90)'),
        "graficar": ("func cobra_graficar", "cobra_graficar(hb)"),
        "corelibs": ('longitud("cobra")',),
        "standard_library": ('mostrar("hola")',),
    },
    "cpp": {
        "holobit": ("auto hb = cobra_holobit({ 1, 2, 3 });",),
        "proyectar": ("inline std::vector<double> cobra_proyectar", 'cobra_proyectar(hb, "2d");'),
        "transformar": ("inline CobraHolobit cobra_transformar", 'cobra_transformar(hb, "rotar", {cobra_runtime_arg(90)});'),
        "graficar": ("inline std::string cobra_graficar", "cobra_graficar(hb);"),
        "corelibs": ('longitud("cobra");',),
        "standard_library": ('mostrar("hola");',),
    },
    "java": {
        "holobit": ("Object hb = cobra_holobit(new double[]{1, 2, 3});",),
        "proyectar": ("private static double[] cobra_proyectar", 'cobra_proyectar(hb, "2d")'),
        "transformar": ("private static CobraHolobit cobra_transformar", 'cobra_transformar(hb, "rotar", 90)'),
        "graficar": ("private static String cobra_graficar", "cobra_graficar(hb);"),
        "corelibs": ('longitud("cobra")',),
        "standard_library": ('mostrar("hola")',),
    },
    "asm": {
        "holobit": ("HOLOBIT hb [1, 2, 3]",),
        "proyectar": ("cobra_proyectar:", "CALL cobra_proyectar hb, '2d'"),
        "transformar": ("cobra_transformar:", "CALL cobra_transformar hb, 'rotar', 90"),
        "graficar": ("cobra_graficar:", "CALL cobra_graficar hb"),
        "corelibs": ("CALL longitud 'cobra'",),
        "standard_library": ("CALL mostrar 'hola'",),
    },
}


CANONICAL_PROGRAM_FIXTURES: Final[dict[str, dict[str, object]]] = {
    "holobit": {
        "description": "Creación canónica de holobit",
        "source": "hb = holobit([1, 2, 3])",
        "nodes": FEATURE_NODES["holobit"](),
    },
    "proyectar": {
        "description": "Proyección canónica sobre holobit",
        "source": "hb = holobit([1, 2, 3])\nproyectar(hb, '2d')",
        "nodes": FEATURE_NODES["proyectar"](),
    },
    "transformar": {
        "description": "Transformación canónica sobre holobit",
        "source": "hb = holobit([1, 2, 3])\ntransformar(hb, 'rotar', 90)",
        "nodes": FEATURE_NODES["transformar"](),
    },
    "graficar": {
        "description": "Graficado canónico de holobit",
        "source": "hb = holobit([1, 2, 3])\ngraficar(hb)",
        "nodes": FEATURE_NODES["graficar"](),
    },
    "corelibs": {
        "description": "Llamada canónica a corelibs",
        "source": "usar corelibs\nlongitud('cobra')",
        "nodes": FEATURE_NODES["corelibs"](),
    },
    "standard_library": {
        "description": "Llamada canónica a standard_library",
        "source": "usar standard_library\nmostrar('hola')",
        "nodes": FEATURE_NODES["standard_library"](),
    },
}

CANONICAL_FULL_PROGRAM_FIXTURE: Final[dict[str, object]] = {
    "description": "Programa canónico integral con holobit + runtime base",
    "source": (
        "usar corelibs\n"
        "usar standard_library\n"
        "hb = holobit([1, 2, 3])\n"
        "proyectar(hb, '2d')\n"
        "transformar(hb, 'rotar', 90)\n"
        "graficar(hb)\n"
        "longitud('cobra')\n"
        "mostrar('hola')"
    ),
    "nodes": [
        NodoHolobit("hb", [1, 2, 3]),
        NodoProyectar(NodoIdentificador("hb"), NodoValor("2d")),
        NodoTransformar(NodoIdentificador("hb"), NodoValor("rotar"), [NodoValor(90)]),
        NodoGraficar(NodoIdentificador("hb")),
        NodoLlamadaFuncion("longitud", [NodoValor("cobra")]),
        NodoLlamadaFuncion("mostrar", [NodoValor("hola")]),
    ],
}

PARTIAL_CONTRACT_ERROR_MARKERS: Final[dict[str, dict[str, tuple[str, ...]]]] = {
    "javascript": {
        "proyectar": (
            "Runtime Holobit JavaScript: feature=${feature}; contrato partial; backend sin holobit_sdk;",
            "throw new Error(",
        ),
        "transformar": (
            "Runtime Holobit JavaScript: feature=${feature}; contrato partial; backend sin holobit_sdk;",
            "throw new Error(",
        ),
        "graficar": (
            "Runtime Holobit JavaScript: feature=${feature}; contrato partial; backend sin holobit_sdk;",
            "throw new Error(",
        ),
    },
    "rust": {
        "proyectar": (
            "Runtime Holobit Rust: feature={}; contrato partial; backend sin holobit_sdk;",
            "cobra_holobit_partial_contract_error(",
        ),
        "transformar": (
            "Runtime Holobit Rust: feature={}; contrato partial; backend sin holobit_sdk;",
            "cobra_holobit_partial_contract_error(",
        ),
        "graficar": (
            "Runtime Holobit Rust: feature={}; contrato partial; backend sin holobit_sdk;",
            "cobra_holobit_partial_contract_error(",
        ),
    },
    "go": {
        "proyectar": (
            "Runtime Holobit Go: feature=%s; contrato partial; backend sin holobit_sdk;",
            "cobraHolobitPartialContractPanic(",
        ),
        "transformar": (
            "Runtime Holobit Go: feature=%s; contrato partial; backend sin holobit_sdk;",
            "cobraHolobitPartialContractPanic(",
        ),
        "graficar": (
            "Runtime Holobit Go: feature=%s; contrato partial; backend sin holobit_sdk;",
            "cobraHolobitPartialContractPanic(",
        ),
    },
    "cpp": {
        "proyectar": (
            "Runtime Holobit C++: feature=\" + feature + \"; contrato partial; backend sin holobit_sdk;",
            "cobra_holobit_partial_contract_error(",
        ),
        "transformar": (
            "Runtime Holobit C++: feature=\" + feature + \"; contrato partial; backend sin holobit_sdk;",
            "cobra_holobit_partial_contract_error(",
        ),
        "graficar": (
            "Runtime Holobit C++: feature=\" + feature + \"; contrato partial; backend sin holobit_sdk;",
            "cobra_holobit_partial_contract_error(",
        ),
    },
    "java": {
        "proyectar": (
            "Runtime Holobit Java: feature=\" + feature + \"; contrato partial; backend sin holobit_sdk;",
            "cobraHolobitPartialContractError(",
        ),
        "transformar": (
            "Runtime Holobit Java: feature=\" + feature + \"; contrato partial; backend sin holobit_sdk;",
            "cobraHolobitPartialContractError(",
        ),
        "graficar": (
            "Runtime Holobit Java: feature=\" + feature + \"; contrato partial; backend sin holobit_sdk;",
            "cobraHolobitPartialContractError(",
        ),
    },
    "wasm": {
        "proyectar": ("backend wasm: contrato partial", "depende del host para la semántica completa"),
        "transformar": ("backend wasm: contrato partial", "depende del host para la semántica completa"),
        "graficar": ("backend wasm: contrato partial", "depende del host para la semántica completa"),
    },
    "asm": {
        "proyectar": ("runtime de inspección/diagnóstico", "TRAP"),
        "transformar": ("runtime de inspección/diagnóstico", "TRAP"),
        "graficar": ("runtime de inspección/diagnóstico", "TRAP"),
    },
}
RUNTIME_HOOK_EXPECTATIONS: Final[dict[str, tuple[str, ...]]] = {
    "python": ("def cobra_holobit", "def cobra_proyectar", "def cobra_transformar", "def cobra_graficar"),
    "javascript": ("function cobra_holobit", "function cobra_proyectar", "function cobra_transformar", "function cobra_graficar"),
    "rust": ("fn cobra_holobit", "fn cobra_proyectar", "fn cobra_transformar", "fn cobra_graficar"),
    "wasm": (
        "(func $cobra_holobit",
        "(func $cobra_proyectar",
        "(func $cobra_transformar",
        "(func $cobra_graficar",
    ),
    "go": ("func cobra_holobit", "func cobra_proyectar", "func cobra_transformar", "func cobra_graficar"),
    "cpp": ("inline CobraHolobit cobra_holobit", "inline std::vector<double> cobra_proyectar", "inline CobraHolobit cobra_transformar", "inline std::string cobra_graficar"),
    "java": (
        "private static CobraHolobit cobra_holobit",
        "private static double[] cobra_proyectar",
        "private static CobraHolobit cobra_transformar",
        "private static String cobra_graficar",
    ),
    "asm": ("cobra_holobit:", "cobra_proyectar:", "cobra_transformar:", "cobra_graficar:"),
}


def generate_code(language: str, feature: str) -> str:
    module_name, class_name = TRANSPILERS[language]
    transpiler_class = getattr(importlib.import_module(module_name), class_name)
    output = transpiler_class().generate_code(FEATURE_NODES[feature]())
    return "\n".join(output) if isinstance(output, list) else str(output)


def canonical_fixture_nodes(feature: str) -> list[object]:
    fixture = CANONICAL_PROGRAM_FIXTURES[feature]
    return list(fixture["nodes"])
