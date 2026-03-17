from __future__ import annotations

"""Utilidades comunes para los transpiladores de Cobra."""

from abc import ABC, abstractmethod
from typing import List, Tuple, Union

from pcobra.core.visitor import NodeVisitor
from pcobra.cobra.transpilers.module_map import get_mapped_path
from pcobra.cobra.transpilers.targets import OFFICIAL_TARGETS


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
    "js": [
        "import * as io from './nativos/io.js';",
        "import * as net from './nativos/red.js';",
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
    "go": [
        'import "cobra/corelibs"',
        'import "cobra/standard_library"',
    ],
    "cpp": [
        "#include <cobra/corelibs.hpp>",
        "#include <cobra/standard_library.hpp>",
    ],
    "java": [
        "import cobra.corelibs.*;",
        "import cobra.standard_library.*;",
    ],
    "wasm": [
        ";; runtime import: corelibs",
        ";; runtime import: standard_library",
    ],
    "asm": [
        "; runtime import corelibs",
        "; runtime import standard_library",
    ],
}


RUNTIME_HOOKS = {
    "js": [
        "function cobra_proyectar(hb, modo) {",
        "    if (hb && typeof hb.proyectar === 'function') {",
        "        return hb.proyectar(modo);",
        "    }",
        "    throw new Error('[cobra::proyectar] Holobit no implementa proyectar(modo) o runtime no configurado correctamente.');",
        "}",
        "function cobra_transformar(hb, op, ...params) {",
        "    if (hb && typeof hb.transformar === 'function') {",
        "        return hb.transformar(op, ...params);",
        "    }",
        "    throw new Error('[cobra::transformar] Holobit no implementa transformar(op, ...params) o runtime no configurado correctamente.');",
        "}",
        "function cobra_graficar(hb) {",
        "    if (hb && typeof hb.graficar === 'function') {",
        "        return hb.graficar();",
        "    }",
        "    throw new Error('[cobra::graficar] Holobit no implementa graficar() o runtime no configurado correctamente.');",
        "}",
    ],
    "rust": [
        "fn cobra_proyectar(hb: &str, modo: &str) {",
        "    println!(\"[cobra::proyectar] {} {}\", hb, modo);",
        "}",
        "fn cobra_transformar(hb: &str, op: &str, params: &[&str]) {",
        "    println!(\"[cobra::transformar] {} {} {:?}\", hb, op, params);",
        "}",
        "fn cobra_graficar(hb: &str) {",
        "    println!(\"[cobra::graficar] {}\", hb);",
        "}",
    ],
    "go": [
        "func cobraProyectar(hb any, modo any) {",
        '    fmt.Printf("[cobra::proyectar] %v %v\\n", hb, modo)',
        "}",
        "func cobraTransformar(hb any, op any, params ...any) {",
        '    fmt.Printf("[cobra::transformar] %v %v %v\\n", hb, op, params)',
        "}",
        "func cobraGraficar(hb any) {",
        '    fmt.Printf("[cobra::graficar] %v\\n", hb)',
        "}",
    ],
    "cpp": [
        "inline void cobra_proyectar(const auto& hb, const auto& modo) {",
        "    std::cout << \"[cobra::proyectar] \" << hb << \" \" << modo << std::endl;",
        "}",
        "inline void cobra_transformar(const auto& hb, const auto& op, std::initializer_list<std::string> params) {",
        "    std::cout << \"[cobra::transformar] \" << hb << \" \" << op << std::endl;",
        "}",
        "inline void cobra_graficar(const auto& hb) {",
        "    std::cout << \"[cobra::graficar] \" << hb << std::endl;",
        "}",
    ],
    "java": [
        "private static void cobraProyectar(Object hb, Object modo) {",
        "    System.out.println(\"[cobra::proyectar] \" + hb + \" \" + modo);",
        "}",
        "private static void cobraTransformar(Object hb, Object op, Object... params) {",
        "    System.out.println(\"[cobra::transformar] \" + hb + \" \" + op);",
        "}",
        "private static void cobraGraficar(Object hb) {",
        "    System.out.println(\"[cobra::graficar] \" + hb);",
        "}",
    ],
    "wasm": [
        ";; runtime hook cobra_proyectar(hb, modo)",
        ";; runtime hook cobra_transformar(hb, op, ...params)",
        ";; runtime hook cobra_graficar(hb)",
    ],
    "asm": [
        "; hook cobra_proyectar hb modo",
        "; hook cobra_transformar hb op ...params",
        "; hook cobra_graficar hb",
    ],
}

for _target in OFFICIAL_TARGETS:
    STANDARD_IMPORTS.setdefault(_target, [])
    RUNTIME_HOOKS.setdefault(_target, [])


def save_file(content: Union[str, List[str]], path: str) -> None:
    """Guarda *content* en la ruta *path*."""
    texto = "\n".join(content) if isinstance(content, list) else str(content)
    with open(path, "w", encoding="utf-8") as archivo:
        archivo.write(texto)


def get_standard_imports(language: str) -> Union[str, List[str]]:
    """Devuelve las importaciones por defecto para *language*."""
    imports = STANDARD_IMPORTS.get(language, [])
    if isinstance(imports, list):
        return list(imports)
    return imports


def get_runtime_hooks(language: str) -> List[str]:
    """Devuelve hooks auxiliares de runtime para *language*."""
    return list(RUNTIME_HOOKS.get(language, []))


def load_mapped_module(path: str, language: str) -> Tuple[str, str]:
    """Carga el módulo indicado respetando el mapeo configurado."""
    ruta = get_mapped_path(path, language)
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
