from __future__ import annotations

"""Utilidades comunes para los transpiladores de Cobra."""

from abc import ABC, abstractmethod
from typing import List, Tuple, Union

from pcobra.core.visitor import NodeVisitor
from pcobra.cobra.transpilers.module_map import get_mapped_path
from pcobra.cobra.transpilers.targets import (
    OFFICIAL_TARGETS,
    normalize_target_name,
    resolution_candidates,
)


class BaseTranspiler(NodeVisitor, ABC):
    """Clase base para los transpiladores que generan código."""

    def __init__(self) -> None:
        self.codigo: Union[str, List[str]] = []

    @abstractmethod
    def generate_code(self, ast):
        """Genera el código a partir del AST proporcionado."""
        raise NotImplementedError

    def save_file(self, path: str) -> None:
        """Guarda el código generado en la ruta dada."""
        save_file(self.codigo, path)


STANDARD_IMPORTS = {
    "python": (
        "from core.nativos import *\n"
        "from corelibs import *\n"
        "from standard_library import *\n"
    ),
    "javascript": [
        "import * as io from './nativos/io.js';",
        "import * as matematicas from './nativos/matematicas.js';",
        "import { Pila, Cola } from './nativos/estructuras.js';",
        "import * as archivo from './nativos/archivo.js';",
        "import * as coleccion from './nativos/coleccion.js';",
        "import * as numero from './nativos/numero.js';",
        "import * as red from './nativos/red.js';",
        "import * as seguridad from './nativos/seguridad.js';",
        "import * as sistema from './nativos/sistema.js';",
        "import * as texto from './nativos/texto.js';",
        "import * as tiempo from './nativos/tiempo.js';",
    ],
    "rust": ["use crate::corelibs::*;", "use crate::standard_library::*;"],
    "go": ["cobra/corelibs", "cobra/standard_library"],
    "cpp": [
        "#include <cobra/corelibs.hpp>",
        "#include <cobra/standard_library.hpp>",
    ],
    "java": [
        "import cobra.corelibs.*;",
        "import cobra.standard_library.*;",
    ],
    "wasm": [
        ";; backend wasm: imports de runtime administrados externamente",
    ],
    "asm": [
        "; backend asm: imports de runtime administrados externamente",
    ],
}


RUNTIME_HOOKS = {
    "python": [
        "def cobra_holobit(valores):",
        "    if 'holobit' in globals() and callable(globals()['holobit']):",
        "        return holobit(valores)",
        "    raise NotImplementedError('Runtime hook holobit no disponible en Python')",
        "",
        "def cobra_proyectar(hb, modo):",
        "    if 'proyectar' in globals() and callable(globals()['proyectar']):",
        "        return proyectar(hb, modo)",
        "    if hasattr(hb, 'proyectar') and callable(getattr(hb, 'proyectar')):",
        "        return hb.proyectar(modo)",
        "    raise NotImplementedError('Runtime hook proyectar no disponible en Python')",
        "",
        "def cobra_transformar(hb, op, *params):",
        "    if 'transformar' in globals() and callable(globals()['transformar']):",
        "        return transformar(hb, op, *params)",
        "    if hasattr(hb, 'transformar') and callable(getattr(hb, 'transformar')):",
        "        return hb.transformar(op, *params)",
        "    raise NotImplementedError('Runtime hook transformar no disponible en Python')",
        "",
        "def cobra_graficar(hb):",
        "    if 'graficar' in globals() and callable(globals()['graficar']):",
        "        return graficar(hb)",
        "    if hasattr(hb, 'graficar') and callable(getattr(hb, 'graficar')):",
        "        return hb.graficar()",
        "    raise NotImplementedError('Runtime hook graficar no disponible en Python')",
    ],
    "javascript": [
        "function cobra_holobit(valores) {",
        "    if (typeof holobit === 'function') {",
        "        return holobit(valores);",
        "    }",
        "    throw new Error('Runtime hook holobit no disponible en JavaScript');",
        "}",
        "function cobra_proyectar(hb, modo) {",
        "    if (hb && typeof hb.proyectar === 'function') {",
        "        return hb.proyectar(modo);",
        "    }",
        "    throw new Error('Runtime hook proyectar no disponible en JavaScript');",
        "}",
        "function cobra_transformar(hb, op, ...params) {",
        "    if (hb && typeof hb.transformar === 'function') {",
        "        return hb.transformar(op, ...params);",
        "    }",
        "    throw new Error('Runtime hook transformar no disponible en JavaScript');",
        "}",
        "function cobra_graficar(hb) {",
        "    if (hb && typeof hb.graficar === 'function') {",
        "        return hb.graficar();",
        "    }",
        "    throw new Error('Runtime hook graficar no disponible en JavaScript');",
        "}",
    ],
    "rust": [
        "fn cobra_holobit(_valores: Vec<f64>) -> Vec<f64> {",
        "    panic!(\"Runtime hook holobit no disponible en Rust\")",
        "}",
        "fn cobra_proyectar(hb: &str, modo: &str) {",
        "    panic!(\"Runtime hook proyectar no disponible en Rust: {} {}\", hb, modo);",
        "}",
        "fn cobra_transformar(hb: &str, op: &str, params: &[&str]) {",
        "    panic!(\"Runtime hook transformar no disponible en Rust: {} {} {:?}\", hb, op, params);",
        "}",
        "fn cobra_graficar(hb: &str) {",
        "    panic!(\"Runtime hook graficar no disponible en Rust: {}\", hb);",
        "}",
    ],
    "go": [
        "func cobraHolobit(valores []float64) []float64 {",
        "    panic(\"runtime hook holobit no disponible en Go\")",
        "}",
        "func cobraProyectar(hb any, modo any) {",
        '    panic(fmt.Sprintf("runtime hook proyectar no disponible en Go: %v %v", hb, modo))',
        "}",
        "func cobraTransformar(hb any, op any, params ...any) {",
        '    panic(fmt.Sprintf("runtime hook transformar no disponible en Go: %v %v %v", hb, op, params))',
        "}",
        "func cobraGraficar(hb any) {",
        '    panic(fmt.Sprintf("runtime hook graficar no disponible en Go: %v", hb))',
        "}",
    ],
    "cpp": [
        "inline auto cobra_holobit(const auto& valores) {",
        "    throw std::runtime_error(\"runtime hook holobit no disponible en C++\");",
        "}",
        "inline void cobra_proyectar(const auto& hb, const auto& modo) {",
        "    throw std::runtime_error(\"runtime hook proyectar no disponible en C++\");",
        "}",
        "inline void cobra_transformar(const auto& hb, const auto& op, std::initializer_list<std::string> params) {",
        "    throw std::runtime_error(\"runtime hook transformar no disponible en C++\");",
        "}",
        "inline void cobra_graficar(const auto& hb) {",
        "    throw std::runtime_error(\"runtime hook graficar no disponible en C++\");",
        "}",
    ],
    "java": [
        "private static Object cobraHolobit(Object valores) {",
        "    throw new UnsupportedOperationException(\"runtime hook holobit no disponible en Java\");",
        "}",
        "private static void cobraProyectar(Object hb, Object modo) {",
        "    throw new UnsupportedOperationException(\"runtime hook proyectar no disponible en Java\");",
        "}",
        "private static void cobraTransformar(Object hb, Object op, Object... params) {",
        "    throw new UnsupportedOperationException(\"runtime hook transformar no disponible en Java\");",
        "}",
        "private static void cobraGraficar(Object hb) {",
        "    throw new UnsupportedOperationException(\"runtime hook graficar no disponible en Java\");",
        "}",
    ],
    "wasm": [
        "(func $cobra_holobit (param $hb i32) (result i32)",
        "  unreachable",
        "  i32.const 0",
        ")",
        "(func $cobra_proyectar (param $hb i32) (param $modo i32)",
        "  unreachable",
        ")",
        "(func $cobra_transformar (param $hb i32) (param $op i32)",
        "  unreachable",
        ")",
        "(func $cobra_graficar (param $hb i32)",
        "  unreachable",
        ")",
    ],
    "asm": [
        "cobra_holobit:",
        "    ; ERROR: runtime hook no implementado",
        "    ud2",
        "cobra_proyectar:",
        "    ; ERROR: runtime hook no implementado",
        "    ud2",
        "cobra_transformar:",
        "    ; ERROR: runtime hook no implementado",
        "    ud2",
        "cobra_graficar:",
        "    ; ERROR: runtime hook no implementado",
        "    ud2",
    ],
}

for _target in OFFICIAL_TARGETS:
    if _target not in STANDARD_IMPORTS:
        raise RuntimeError(f"STANDARD_IMPORTS no define entradas para target '{_target}'")
    if _target not in RUNTIME_HOOKS:
        raise RuntimeError(f"RUNTIME_HOOKS no define entradas para target '{_target}'")


def save_file(content: Union[str, List[str]], path: str) -> None:
    """Guarda *content* en la ruta *path*."""
    texto = "\n".join(content) if isinstance(content, list) else str(content)
    with open(path, "w", encoding="utf-8") as archivo:
        archivo.write(texto)


def get_standard_imports(language: str) -> Union[str, List[str]]:
    """Devuelve las importaciones por defecto para *language*."""
    target = normalize_target_name(language)
    if target not in STANDARD_IMPORTS:
        raise ValueError(f"Target sin STANDARD_IMPORTS configurado: {language}")
    imports = STANDARD_IMPORTS[target]
    if isinstance(imports, list):
        return list(imports)
    return imports


def get_runtime_hooks(language: str) -> List[str]:
    """Devuelve hooks auxiliares de runtime para *language*."""
    target = normalize_target_name(language)
    if target not in RUNTIME_HOOKS:
        raise ValueError(f"Target sin RUNTIME_HOOKS configurado: {language}")
    return list(RUNTIME_HOOKS[target])


def load_mapped_module(path: str, language: str) -> Tuple[str, str]:
    """Carga el módulo indicado respetando el mapeo configurado."""
    ruta = path
    for candidate in resolution_candidates(language):
        ruta_candidate = get_mapped_path(path, candidate)
        if ruta_candidate != path:
            ruta = ruta_candidate
            break
    with open(ruta, "r", encoding="utf-8") as f:
        contenido = f.read()
    return contenido, ruta


__all__ = [
    "BaseTranspiler",
    "save_file",
    "get_standard_imports",
    "get_runtime_hooks",
    "load_mapped_module",
    "STANDARD_IMPORTS",
    "RUNTIME_HOOKS",
]
