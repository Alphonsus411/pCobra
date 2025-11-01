"""Utilidades compartidas para validar y analizar importaciones de módulos Cobra."""

from __future__ import annotations

import os
from functools import lru_cache
from typing import Iterable, FrozenSet, Tuple

from pcobra.cobra.core import Lexer, Parser
from .ast_nodes import NodoAsignacion, NodoClase, NodoFuncion, NodoExport

# Ruta por defecto donde se instalan los módulos empaquetados junto al CLI.
MODULES_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "cli", "modules")
)

# Lista blanca global que permite rutas adicionales durante la ejecución de pruebas
# o cuando el usuario desea importar módulos propios.
IMPORT_WHITELIST: set[str] = set()


def _normalizar_rutas(ruta: str) -> tuple[str, str]:
    """Devuelve la ruta absoluta y su resolución real (sin enlaces simbólicos)."""

    ruta_abs = os.path.abspath(ruta)
    ruta_real = os.path.realpath(ruta_abs)
    return ruta_abs, ruta_real


def ruta_import_permitida(
    ruta: str,
    modules_path: str | None = None,
    whitelist: Iterable[str] | None = None,
) -> bool:
    """Comprueba si ``ruta`` está dentro de los directorios permitidos."""

    ruta_abs, ruta_real = _normalizar_rutas(ruta)
    allowed_roots = []
    base_modules = modules_path if modules_path is not None else MODULES_PATH
    if base_modules:
        allowed_roots.append(base_modules)
    extras = whitelist if whitelist is not None else IMPORT_WHITELIST
    allowed_roots.extend(extras)

    for root in allowed_roots:
        if not root:
            continue
        root_abs, root_real = _normalizar_rutas(root)
        try:
            if (
                os.path.commonpath([ruta_abs, root_abs]) == root_abs
                and os.path.commonpath([ruta_real, root_real]) == root_real
            ):
                return True
        except ValueError:
            # Puede ocurrir en rutas de diferentes unidades (Windows). En ese caso
            # ``commonpath`` falla y la ruta no pertenece al directorio permitido.
            continue
    return False


def _leer_codigo_modulo(
    ruta: str,
    modules_path: str | None = None,
    whitelist: Iterable[str] | None = None,
) -> tuple[str, str]:
    """Lee el código fuente de un módulo Cobra asegurando permisos válidos."""

    ruta_abs, ruta_real = _normalizar_rutas(ruta)
    if not ruta_import_permitida(ruta_abs, modules_path, whitelist):
        raise PermissionError(f"Módulo fuera de la lista blanca: {ruta}")

    try:
        with open(ruta_real, "r", encoding="utf-8") as handler:
            return handler.read(), ruta_real
    except FileNotFoundError as exc:  # pragma: no cover - se vuelve a lanzar abajo
        raise FileNotFoundError(ruta) from exc


def cargar_ast_modulo(
    ruta: str,
    *,
    modules_path: str | None = None,
    whitelist: Iterable[str] | None = None,
):
    """Parsa un módulo Cobra y devuelve su AST."""

    codigo, ruta_real = _leer_codigo_modulo(ruta, modules_path, whitelist)
    lexer = Lexer(codigo)
    tokens = lexer.analizar_token()
    parser = Parser(tokens)
    return parser.parsear()


def _extraer_simbolos(ast_modulo: Iterable) -> FrozenSet[Tuple[str, str]]:
    """Obtiene los símbolos exportables presentes en un AST de módulo."""

    exportados = {
        nodo.nombre for nodo in ast_modulo if isinstance(nodo, NodoExport)
    }

    simbolos: set[Tuple[str, str]] = set()

    def registrar(nombre: object, tipo: str) -> None:
        if not isinstance(nombre, str) or not nombre:
            return
        if exportados and nombre not in exportados:
            return
        simbolos.add((nombre, tipo))

    for nodo in ast_modulo:
        if isinstance(nodo, NodoAsignacion):
            registrar(getattr(nodo, "identificador", nodo.variable), "variable")
        elif isinstance(nodo, NodoFuncion):
            registrar(nodo.nombre, "funcion")
        elif isinstance(nodo, NodoClase):
            registrar(nodo.nombre, "clase")

    return frozenset(simbolos)


@lru_cache(maxsize=128)
def _simbolos_modulo_cache(ruta_real: str) -> FrozenSet[Tuple[str, str]]:
    """Versión cacheada de :func:`_extraer_simbolos` basada en la ruta real."""

    ast_modulo = cargar_ast_modulo(ruta_real)
    return _extraer_simbolos(ast_modulo)


def obtener_simbolos_modulo(ruta: str) -> set[Tuple[str, str]]:
    """Devuelve los símbolos declarados exportables de un módulo Cobra."""

    _, ruta_real = _normalizar_rutas(ruta)
    return set(_simbolos_modulo_cache(ruta_real))
