"""Utilidades para gestionar importaciones en los transpiladores."""

from __future__ import annotations

from typing import List, Tuple, Union

from .module_map import get_mapped_path

# Mapeo de importaciones estándar por lenguaje
STANDARD_IMPORTS = {
    "python": "from src.core.nativos import *\n",
    "js": [
        "import * as io from './nativos/io.js';",
        "import * as net from './nativos/io.js';",
        "import * as matematicas from './nativos/matematicas.js';",
        "import { Pila, Cola } from './nativos/estructuras.js';",
    ],
}


def get_standard_imports(language: str) -> Union[str, List[str]]:
    """Devuelve las importaciones por defecto para *language*.

    Parameters
    ----------
    language: str
        Identificador del backend (``python``, ``js``...).
    """
    imports = STANDARD_IMPORTS.get(language, [])
    if isinstance(imports, list):
        return list(imports)
    return imports


def load_mapped_module(path: str, language: str) -> Tuple[str, str]:
    """Carga el módulo indicado respetando el mapeo configurado.

    Parameters
    ----------
    path: str
        Ruta declarada en la instrucción ``import``.
    language: str
        Lenguaje de destino para el cual se busca el archivo.

    Returns
    -------
    Tuple[str, str]
        Una tupla ``(contenido, ruta)`` con el código del módulo y la ruta
        real utilizada.
    """
    ruta = get_mapped_path(path, language)
    with open(ruta, "r", encoding="utf-8") as f:
        contenido = f.read()
    return contenido, ruta
