from __future__ import annotations

"""Utilidades comunes para los transpiladores de Cobra."""

from abc import ABC, abstractmethod
from typing import List, Tuple, Union

from core.visitor import NodeVisitor
from cobra.transpilers.module_map import get_mapped_path

# ---------------------------------------------------------------------------
# Clases base
# ---------------------------------------------------------------------------


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


# ---------------------------------------------------------------------------
# Funciones de utilidad
# ---------------------------------------------------------------------------


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
    "swift": [],
    "perl": [],
    "visualbasic": [],
}


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
    "load_mapped_module",
    "STANDARD_IMPORTS",
]
