from __future__ import annotations

"""Utilidades comunes para los transpiladores de Cobra."""

from abc import ABC, abstractmethod
import re
from typing import List, Tuple, Union

from pcobra.core.visitor import NodeVisitor
from pcobra.cobra.transpilers.compatibility_matrix import CONTRACT_FEATURES
from pcobra.cobra.transpilers.module_map import get_mapped_path
from pcobra.cobra.transpilers.target_utils import normalize_target_name
from pcobra.cobra.transpilers.targets import OFFICIAL_TARGETS
from pcobra.cobra.transpilers.transpiler.js_nodes.runtime_holobit import (
    build_holobit_runtime_lines as build_javascript_holobit_runtime_lines,
    build_standard_runtime_lines as build_javascript_standard_runtime_lines,
)
from pcobra.cobra.transpilers.transpiler.rust_nodes.runtime_holobit import (
    build_holobit_runtime_lines as build_rust_holobit_runtime_lines,
    build_standard_runtime_lines as build_rust_standard_runtime_lines,
)
from pcobra.cobra.transpilers.transpiler.go_nodes.runtime_holobit import (
    build_holobit_runtime_lines as build_go_holobit_runtime_lines,
)
from pcobra.cobra.transpilers.transpiler.cpp_nodes.runtime_holobit import (
    build_holobit_runtime_lines as build_cpp_holobit_runtime_lines,
)
from pcobra.cobra.transpilers.transpiler.java_nodes.runtime_holobit import (
    build_holobit_runtime_lines as build_java_holobit_runtime_lines,
)
from pcobra.cobra.transpilers.transpiler.asm_nodes.runtime_holobit import (
    build_holobit_runtime_lines as build_asm_holobit_runtime_lines,
)
from pcobra.cobra.transpilers.transpiler.wasm_runtime import (
    build_holobit_runtime_lines as build_wasm_holobit_runtime_lines,
    build_standard_runtime_lines as build_wasm_standard_runtime_lines,
)

HOLOBIT_RUNTIME_NODE_TYPES = (
    "NodoHolobit",
    "NodoProyectar",
    "NodoTransformar",
    "NodoGraficar",
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
        *build_javascript_standard_runtime_lines(),
    ],
    "rust": build_rust_standard_runtime_lines(),
    "go": ['_ "pcobra/corelibs"', '_ "pcobra/standard_library"'],
    "cpp": [
        "#include <pcobra/corelibs.hpp>",
        "#include <pcobra/standard_library.hpp>",
    ],
    "java": [
        "import pcobra.corelibs.*;",
        "import pcobra.standard_library.*;",
    ],
    "wasm": build_wasm_standard_runtime_lines(),
    "asm": [
        "; backend asm: imports de runtime administrados externamente",
    ],
}

HOOK_SIGNATURE_MARKERS = {
    "python": {
        "holobit": "def cobra_holobit(",
        "proyectar": "def cobra_proyectar(",
        "transformar": "def cobra_transformar(",
        "graficar": "def cobra_graficar(",
    },
    "javascript": {
        "holobit": "function cobra_holobit(",
        "proyectar": "function cobra_proyectar(",
        "transformar": "function cobra_transformar(",
        "graficar": "function cobra_graficar(",
    },
    "rust": {
        "holobit": "fn cobra_holobit(",
        "proyectar": "fn cobra_proyectar(",
        "transformar": "fn cobra_transformar(",
        "graficar": "fn cobra_graficar(",
    },
    "go": {
        "holobit": "func cobra_holobit(",
        "proyectar": "func cobra_proyectar(",
        "transformar": "func cobra_transformar(",
        "graficar": "func cobra_graficar(",
    },
    "cpp": {
        "holobit": "inline CobraHolobit cobra_holobit(",
        "proyectar": "inline std::vector<double> cobra_proyectar(",
        "transformar": "inline CobraHolobit cobra_transformar(",
        "graficar": "inline std::string cobra_graficar(",
    },
    "java": {
        "holobit": "private static CobraHolobit cobra_holobit(",
        "proyectar": "private static double[] cobra_proyectar(",
        "transformar": "private static CobraHolobit cobra_transformar(",
        "graficar": "private static String cobra_graficar(",
    },
    "wasm": {
        "holobit": "(func $cobra_holobit",
        "proyectar": "(func $cobra_proyectar",
        "transformar": "(func $cobra_transformar",
        "graficar": "(func $cobra_graficar",
    },
    "asm": {
        "holobit": "cobra_holobit:",
        "proyectar": "cobra_proyectar:",
        "transformar": "cobra_transformar:",
        "graficar": "cobra_graficar:",
    },
}


RUNTIME_ERROR_MESSAGE = {
    "python": "Runtime Holobit Python: '{feature}' requiere 'holobit_sdk', dependencia obligatoria de pcobra en Python >=3.10.",
    "javascript": "Runtime Holobit JavaScript: feature={feature}; contrato partial; backend sin holobit_sdk; el adaptador oficial no equivale a la semántica completa de Python.",
    "rust": "Runtime Holobit Rust: feature={feature}; contrato partial; backend sin holobit_sdk; el adaptador oficial no equivale a la semántica completa de Python.",
    "go": "Runtime Holobit Go: feature={feature}; contrato partial; backend sin holobit_sdk; el adaptador oficial no equivale a la semántica completa de Python.",
    "cpp": "Runtime Holobit C++: feature={feature}; contrato partial; backend sin holobit_sdk; el adaptador oficial no equivale a la semántica completa de Python.",
    "java": "Runtime Holobit Java: feature={feature}; contrato partial; backend sin holobit_sdk; el adaptador oficial no equivale a la semántica completa de Python.",
    "wasm": "Runtime Holobit WASM: feature={feature}; contrato partial; backend host-managed sin holobit_sdk dentro del módulo generado.",
    "asm": "Runtime Holobit ASM: feature={feature}; contrato partial; backend de inspección/diagnóstico sin holobit_sdk ni runtime embebido.",
}


RUNTIME_HOOKS = {
    "python": [
        "def _cobra_missing_holobit(feature):",
        "    raise ModuleNotFoundError(",
        "        f\"Runtime Holobit Python: '{feature}' requiere 'holobit_sdk', dependencia obligatoria de pcobra en Python >=3.10.\"",
        "    )",
        "",
        "def _cobra_import_holobit_runtime():",
        "    from pcobra.core.holobits import Holobit, proyectar, transformar, graficar",
        "    return Holobit, proyectar, transformar, graficar",
        "",
        "def cobra_holobit(valores):",
        "    Holobit, _, _, _ = _cobra_import_holobit_runtime()",
        "    return Holobit(valores)",
        "",
        "def cobra_proyectar(hb, modo):",
        "    _, proyectar, _, _ = _cobra_import_holobit_runtime()",
        "    try:",
        "        return proyectar(hb, modo)",
        "    except ModuleNotFoundError as exc:",
        "        if 'holobit_sdk' not in str(exc):",
        "            raise ModuleNotFoundError(",
        "                f\"Runtime Holobit Python: 'proyectar' requiere 'holobit_sdk', dependencia obligatoria de pcobra en Python >=3.10.\"",
        "            ) from exc",
        "        raise",
        "",
        "def cobra_transformar(hb, op, *params):",
        "    _, _, transformar, _ = _cobra_import_holobit_runtime()",
        "    try:",
        "        return transformar(hb, op, *params)",
        "    except ModuleNotFoundError as exc:",
        "        if 'holobit_sdk' not in str(exc):",
        "            raise ModuleNotFoundError(",
        "                f\"Runtime Holobit Python: 'transformar' requiere 'holobit_sdk', dependencia obligatoria de pcobra en Python >=3.10.\"",
        "            ) from exc",
        "        raise",
        "",
        "def cobra_graficar(hb):",
        "    _, _, _, graficar = _cobra_import_holobit_runtime()",
        "    try:",
        "        return graficar(hb)",
        "    except ModuleNotFoundError as exc:",
        "        if 'holobit_sdk' not in str(exc):",
        "            raise ModuleNotFoundError(",
        "                f\"Runtime Holobit Python: 'graficar' requiere 'holobit_sdk', dependencia obligatoria de pcobra en Python >=3.10.\"",
        "            ) from exc",
        "        raise",
    ],
    "javascript": build_javascript_holobit_runtime_lines(),
    "rust": build_rust_holobit_runtime_lines(),
    "go": build_go_holobit_runtime_lines(),
    "cpp": build_cpp_holobit_runtime_lines(),
    "java": build_java_holobit_runtime_lines(),
    "wasm": build_wasm_holobit_runtime_lines(),
    "asm": build_asm_holobit_runtime_lines(),
}


MINIMAL_RUNTIME_ROUTE_MARKERS = {
    "python": {
        "corelibs": "from corelibs import *",
        "standard_library": "from standard_library import *",
        "minimal_symbols": (),
    },
    "javascript": {
        "corelibs": "import * as coleccion from './nativos/coleccion.js';",
        "standard_library": "const mostrar = (...args) => cobraJsStandardLibrary.mostrar(...args);",
        "minimal_symbols": (
            "const longitud = (valor) => cobraJsCorelibs.longitud(valor);",
            "const mostrar = (...args) => cobraJsStandardLibrary.mostrar(...args);",
        ),
    },
    "rust": {
        "corelibs": "use crate::corelibs::*;",
        "standard_library": "use crate::standard_library::*;",
        "minimal_symbols": ("fn longitud<T: ToString>(valor: T) -> usize {", "fn mostrar<T: Display>(valor: T) {"),
    },
    "wasm": {
        "corelibs": '(import "pcobra:corelibs" "longitud"',
        "standard_library": '(import "pcobra:standard_library" "mostrar"',
        "minimal_symbols": ("(func $longitud", "(func $mostrar"),
    },
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
    "asm": {
        "corelibs": "; backend asm: imports de runtime administrados externamente",
        "standard_library": "runtime externo",
        "minimal_symbols": ("cobra_proyectar:", "TRAP"),
    },
}


def validate_runtime_contracts() -> None:
    """Valida imports/hooks de runtime para todos los backends oficiales."""
    holobit_features = CONTRACT_FEATURES[:4]
    advanced_features = CONTRACT_FEATURES[1:4]
    for target in OFFICIAL_TARGETS:
        if target not in STANDARD_IMPORTS:
            raise RuntimeError(
                f"STANDARD_IMPORTS no define entradas para target '{target}'"
            )
        if target not in RUNTIME_HOOKS:
            raise RuntimeError(
                f"RUNTIME_HOOKS no define entradas para target '{target}'"
            )
        if target not in HOOK_SIGNATURE_MARKERS:
            raise RuntimeError(
                f"HOOK_SIGNATURE_MARKERS no define firmas para target '{target}'"
            )

        imports = STANDARD_IMPORTS[target]
        if isinstance(imports, str):
            if not imports.strip():
                raise RuntimeError(
                    f"STANDARD_IMPORTS['{target}'] no puede ser una cadena vacía"
                )
        elif not imports:
            raise RuntimeError(
                f"STANDARD_IMPORTS['{target}'] no puede ser una lista vacía"
            )

        hooks = RUNTIME_HOOKS[target]
        if not hooks:
            raise RuntimeError(
                f"RUNTIME_HOOKS['{target}'] debe definir hooks cobra_* para Holobit"
            )

        hook_blob = "\n".join(hooks)
        for feature in holobit_features:
            marker = HOOK_SIGNATURE_MARKERS[target][feature]
            if marker not in hook_blob:
                raise RuntimeError(
                    f"RUNTIME_HOOKS['{target}'] no contiene la firma esperada "
                    f"para {feature}: {marker}"
                )

        for feature in advanced_features:
            expected_error = RUNTIME_ERROR_MESSAGE[target].format(feature=feature)
            if target == "python":
                if expected_error not in hook_blob:
                    raise RuntimeError(
                        f"RUNTIME_HOOKS['{target}'] no contiene el error explícito "
                        f"esperado para {feature}: {expected_error}"
                    )
                continue

        if target in {"javascript", "rust", "go", "cpp", "java"}:
            required_markers = (
                "contrato partial",
                "holobit_sdk",
                "semántica completa de Python",
            )
            for marker in required_markers:
                if marker not in hook_blob:
                    raise RuntimeError(
                        f"RUNTIME_HOOKS['{target}'] no contiene la nota contractual explícita requerida: {marker}"
                    )

        if target == "wasm":
            required_markers = (
                "contrato partial",
                "host-managed",
                "holobit_sdk",
            )
            for marker in required_markers:
                if marker not in hook_blob:
                    raise RuntimeError(
                        f"RUNTIME_HOOKS['{target}'] no contiene la nota contractual explícita requerida: {marker}"
                    )

        if target == "asm":
            required_markers = (
                "contrato partial",
                "inspección/diagnóstico",
                "holobit_sdk",
            )
            for marker in required_markers:
                if marker not in hook_blob:
                    raise RuntimeError(
                        f"RUNTIME_HOOKS['{target}'] no contiene la nota contractual explícita requerida: {marker}"
                    )

        if target == "asm" and "backend de inspección/diagnóstico" not in hook_blob:
            raise RuntimeError(
                "RUNTIME_HOOKS['asm'] debe declararse explícitamente como backend de inspección/diagnóstico"
            )

        forbidden_markers = ("cobra_escalar", "cobra_mover")
        for forbidden_marker in forbidden_markers:
            if forbidden_marker in hook_blob:
                raise RuntimeError(
                    f"RUNTIME_HOOKS['{target}'] no debe exponer hooks fuera del "
                    f"contrato Holobit transversal: {forbidden_marker}"
                )

        if target != "python":
            forbidden_runtime_routes = (
                r"\bcobra\.",
                r"\bcobra/corelibs",
                r"\bcobra/standard_library",
                r"\bcobra/core",
            )
            combined_blob = "\n".join(
                [
                    imports if isinstance(imports, str) else "\n".join(imports),
                    hook_blob,
                ]
            )
            for forbidden_route in forbidden_runtime_routes:
                if re.search(forbidden_route, combined_blob):
                    raise RuntimeError(
                        f"Runtime contractual inválido en target '{target}': se detectó ruta no canónica {forbidden_route!r}; "
                        "usar siempre namespace runtime `pcobra` en backends no Python."
                    )


def validate_minimal_runtime_routes() -> None:
    """Valida rutas mínimas `corelibs`/`standard_library` por backend oficial."""
    for target in OFFICIAL_TARGETS:
        if target not in MINIMAL_RUNTIME_ROUTE_MARKERS:
            raise RuntimeError(
                f"MINIMAL_RUNTIME_ROUTE_MARKERS no define reglas para target '{target}'"
            )

        markers = MINIMAL_RUNTIME_ROUTE_MARKERS[target]
        imports = get_standard_imports(target)
        hooks = "\n".join(get_runtime_hooks(target))
        import_blob = imports if isinstance(imports, str) else "\n".join(imports)
        combined = f"{import_blob}\n{hooks}"

        for feature in ("corelibs", "standard_library"):
            marker = markers[feature]
            if marker not in combined:
                raise RuntimeError(
                    f"Contrato mínimo incumplido en target '{target}' para '{feature}': "
                    f"falta marcador {marker!r}"
                )

        for symbol_marker in markers["minimal_symbols"]:
            if symbol_marker not in combined:
                raise RuntimeError(
                    f"Target '{target}' no expone símbolos mínimos ni error explícito esperado: "
                    f"falta marcador {symbol_marker!r}"
                )


validate_runtime_contracts()


def ast_contains_node_types(tree, node_type_names: tuple[str, ...]) -> bool:
    """Indica si ``tree`` contiene algún nodo cuyo nombre de clase esté en ``node_type_names``."""
    if tree is None:
        return False
    if isinstance(tree, (list, tuple, set)):
        return any(ast_contains_node_types(item, node_type_names) for item in tree)
    if tree.__class__.__name__ in node_type_names:
        return True
    for value in getattr(tree, "__dict__", {}).values():
        if ast_contains_node_types(value, node_type_names):
            return True
    return False


def ast_requires_holobit_runtime(tree) -> bool:
    """Indica si ``tree`` requiere inyección del runtime Holobit contractual."""
    return ast_contains_node_types(tree, HOLOBIT_RUNTIME_NODE_TYPES)


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
    ruta = get_mapped_path(path, language)
    with open(ruta, "r", encoding="utf-8") as f:
        contenido = f.read()
    return contenido, ruta


validate_minimal_runtime_routes()


__all__ = [
    "BaseTranspiler",
    "save_file",
    "get_standard_imports",
    "get_runtime_hooks",
    "load_mapped_module",
    "STANDARD_IMPORTS",
    "RUNTIME_HOOKS",
    "HOOK_SIGNATURE_MARKERS",
    "RUNTIME_ERROR_MESSAGE",
    "validate_runtime_contracts",
    "validate_minimal_runtime_routes",
    "MINIMAL_RUNTIME_ROUTE_MARKERS",
    "ast_contains_node_types",
    "HOLOBIT_RUNTIME_NODE_TYPES",
    "ast_requires_holobit_runtime",
]
