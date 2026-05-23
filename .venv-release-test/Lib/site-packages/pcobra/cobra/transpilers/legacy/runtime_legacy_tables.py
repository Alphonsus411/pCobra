"""Tablas legacy de backends no oficiales (sin uso en arranque normal)."""

from __future__ import annotations

LEGACY_BACKENDS = ("go", "cpp", "java", "wasm", "asm")

LEGACY_RUNTIME_ERROR_MESSAGE = {
    "go": "Runtime Holobit Go: feature={feature}; contrato partial; backend sin holobit_sdk; el adaptador oficial no equivale a la semántica completa de Python.",
    "cpp": "Runtime Holobit C++: feature={feature}; contrato partial; backend sin holobit_sdk; el adaptador oficial no equivale a la semántica completa de Python.",
    "java": "Runtime Holobit Java: feature={feature}; contrato partial; backend sin holobit_sdk; el adaptador oficial no equivale a la semántica completa de Python.",
    "wasm": "Runtime Holobit WASM: feature={feature}; contrato partial; backend host-managed sin holobit_sdk dentro del módulo generado.",
    "asm": "Runtime Holobit ASM: feature={feature}; contrato partial; backend de inspección/diagnóstico sin holobit_sdk ni runtime embebido.",
}

LEGACY_MINIMAL_RUNTIME_ROUTE_MARKERS = {
    "go": {
        "corelibs": '"pcobra/corelibs"',
        "standard_library": '"pcobra/standard_library"',
        "minimal_symbols": ("func longitud(valor any) int {", "func mostrar(valores ...any) any {"),
    },
    "cpp": {
        "corelibs": "#include <pcobra/corelibs.hpp>",
        "standard_library": "#include <pcobra/standard_library.hpp>",
        "minimal_symbols": ("inline std::size_t longitud(const T& valor) {", "inline T mostrar(const T& valor) {"),
    },
    "java": {
        "corelibs": "import pcobra.corelibs.*;",
        "standard_library": "import pcobra.standard_library.*;",
        "minimal_symbols": ("private static int longitud(Object valor) {", "private static Object mostrar(Object... valores) {"),
    },
    "wasm": {
        "corelibs": '(import "pcobra:corelibs" "longitud"',
        "standard_library": '(import "pcobra:standard_library" "mostrar"',
        "minimal_symbols": ("(func $longitud", "(func $mostrar"),
    },
    "asm": {
        "corelibs": "; backend asm: imports de runtime administrados externamente",
        "standard_library": "runtime externo",
        "minimal_symbols": ("cobra_proyectar:", "TRAP"),
    },
}
