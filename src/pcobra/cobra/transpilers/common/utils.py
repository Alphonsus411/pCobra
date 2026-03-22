from __future__ import annotations

"""Utilidades comunes para los transpiladores de Cobra."""

from abc import ABC, abstractmethod
from typing import List, Tuple, Union

from pcobra.core.visitor import NodeVisitor
from pcobra.cobra.transpilers.compatibility_matrix import CONTRACT_FEATURES
from pcobra.cobra.transpilers.module_map import get_mapped_path
from pcobra.cobra.transpilers.targets import (
    OFFICIAL_TARGETS,
    normalize_target_name,
)
from pcobra.cobra.transpilers.transpiler.js_nodes.runtime_holobit import (
    build_holobit_runtime_lines as build_javascript_holobit_runtime_lines,
    build_standard_runtime_lines as build_javascript_standard_runtime_lines,
)
from pcobra.cobra.transpilers.transpiler.rust_nodes.runtime_holobit import (
    build_holobit_runtime_lines as build_rust_holobit_runtime_lines,
    build_standard_runtime_lines as build_rust_standard_runtime_lines,
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
    "go": ["cobra/corelibs", "cobra/standard_library"],
    "cpp": [
        "#include <cobra/corelibs.hpp>",
        "#include <cobra/standard_library.hpp>",
    ],
    "java": [
        "import cobra.corelibs.*;",
        "import cobra.standard_library.*;",
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
        "holobit": "inline auto cobra_holobit(",
        "proyectar": "inline void cobra_proyectar(",
        "transformar": "inline void cobra_transformar(",
        "graficar": "inline void cobra_graficar(",
    },
    "java": {
        "holobit": "private static Object cobra_holobit(",
        "proyectar": "private static void cobra_proyectar(",
        "transformar": "private static void cobra_transformar(",
        "graficar": "private static void cobra_graficar(",
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
    "javascript": "Runtime Holobit JavaScript: '{feature}' requiere runtime avanzado compatible.",
    "rust": "Runtime Holobit Rust: '{feature}' requiere runtime avanzado compatible.",
    "go": "Runtime Holobit Go: '{feature}' requiere runtime avanzado compatible.",
    "cpp": "Runtime Holobit C++: '{feature}' requiere runtime avanzado compatible.",
    "java": "Runtime Holobit Java: '{feature}' requiere runtime avanzado compatible.",
    "wasm": "Runtime Holobit WASM: '{feature}' requiere runtime avanzado compatible.",
    "asm": "Runtime Holobit ASM: '{feature}' requiere runtime avanzado compatible.",
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
    "go": [
        "func cobra_holobit(valores []float64) []float64 {",
        "    return valores",
        "}",
        "func cobra_proyectar(hb any, modo any) {",
        '    panic(fmt.Sprintf("Runtime Holobit Go: \'proyectar\' requiere runtime avanzado compatible. hb=%v modo=%v", hb, modo))',
        "}",
        "func cobra_transformar(hb any, op any, params ...any) {",
        '    panic(fmt.Sprintf("Runtime Holobit Go: \'transformar\' requiere runtime avanzado compatible. hb=%v op=%v params=%v", hb, op, params))',
        "}",
        "func cobra_graficar(hb any) {",
        '    panic(fmt.Sprintf("Runtime Holobit Go: \'graficar\' requiere runtime avanzado compatible. hb=%v", hb))',
        "}",
    ],
    "cpp": [
        "inline auto cobra_holobit(const auto& valores) {",
        "    return valores;",
        "}",
        "inline void cobra_proyectar(const auto& hb, const auto& modo) {",
        "    throw std::runtime_error(\"Runtime Holobit C++: 'proyectar' requiere runtime avanzado compatible.\");",
        "}",
        "inline void cobra_transformar(const auto& hb, const auto& op, std::initializer_list<std::string> params) {",
        "    throw std::runtime_error(\"Runtime Holobit C++: 'transformar' requiere runtime avanzado compatible.\");",
        "}",
        "inline void cobra_graficar(const auto& hb) {",
        "    throw std::runtime_error(\"Runtime Holobit C++: 'graficar' requiere runtime avanzado compatible.\");",
        "}",
    ],
    "java": [
        "private static Object cobra_holobit(Object valores) {",
        "    return valores;",
        "}",
        "private static void cobra_proyectar(Object hb, Object modo) {",
        "    throw new UnsupportedOperationException(\"Runtime Holobit Java: 'proyectar' requiere runtime avanzado compatible.\");",
        "}",
        "private static void cobra_transformar(Object hb, Object op, Object... params) {",
        "    throw new UnsupportedOperationException(\"Runtime Holobit Java: 'transformar' requiere runtime avanzado compatible.\");",
        "}",
        "private static void cobra_graficar(Object hb) {",
        "    throw new UnsupportedOperationException(\"Runtime Holobit Java: 'graficar' requiere runtime avanzado compatible.\");",
        "}",
    ],
    "wasm": build_wasm_holobit_runtime_lines(),
    "asm": [
        "cobra_holobit:",
        "    ; Runtime Holobit ASM: 'holobit' conserva el valor de entrada cuando no existe runtime avanzado.",
        "    RET",
        "cobra_proyectar:",
        "    ; Runtime Holobit ASM: 'proyectar' requiere runtime avanzado compatible.",
        "    TRAP",
        "cobra_transformar:",
        "    ; Runtime Holobit ASM: 'transformar' requiere runtime avanzado compatible.",
        "    TRAP",
        "cobra_graficar:",
        "    ; Runtime Holobit ASM: 'graficar' requiere runtime avanzado compatible.",
        "    TRAP",
    ],
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
            if target in {"python", "go", "cpp", "java", "asm"}:
                expected_error = RUNTIME_ERROR_MESSAGE[target].format(feature=feature)
                if expected_error not in hook_blob:
                    raise RuntimeError(
                        f"RUNTIME_HOOKS['{target}'] no contiene el error explícito "
                        f"esperado para {feature}: {expected_error}"
                    )

        forbidden_markers = ("cobra_escalar", "cobra_mover")
        for forbidden_marker in forbidden_markers:
            if forbidden_marker in hook_blob:
                raise RuntimeError(
                    f"RUNTIME_HOOKS['{target}'] no debe exponer hooks fuera del "
                    f"contrato Holobit transversal: {forbidden_marker}"
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
    "ast_contains_node_types",
    "HOLOBIT_RUNTIME_NODE_TYPES",
    "ast_requires_holobit_runtime",
]
