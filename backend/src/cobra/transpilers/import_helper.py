"""Utilidades para gestionar importaciones en los transpiladores."""

from __future__ import annotations

from typing import List, Tuple, Union

from src.cobra.transpilers.module_map import get_mapped_path

# Mapeo de importaciones estándar por lenguaje
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
