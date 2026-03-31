"""Utilidades compartidas para validar y analizar importaciones de módulos Cobra."""

from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path
from typing import Iterable, FrozenSet, Tuple

from pcobra.core.lexer import Lexer
from pcobra.core.parser import Parser
from .ast_nodes import NodoAsignacion, NodoClase, NodoFuncion, NodoExport

# Ruta por defecto donde se instalan los módulos del usuario.
MODULES_PATH = Path.home() / ".cobra" / "modules"

# Lista blanca global que permite rutas adicionales durante la ejecución de pruebas
# o cuando el usuario desea importar módulos propios.
IMPORT_WHITELIST: set[str | os.PathLike[str]] = {MODULES_PATH}
FingerprintArchivo = tuple[int, int]


class _ArchivoModuloInestableError(RuntimeError):
    """Error interno para reintentar cuando el módulo cambia durante su lectura."""


def _normalizar_rutas(ruta: str) -> tuple[str, str]:
    """Devuelve la ruta absoluta y su resolución real (sin enlaces simbólicos)."""

    ruta_abs = os.path.abspath(os.fspath(ruta))
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


def _fingerprint_archivo(ruta_real: str) -> FingerprintArchivo:
    """Obtiene metadatos estables de versión para invalidar caché por archivo."""

    try:
        stat = os.stat(ruta_real)
    except FileNotFoundError as exc:
        raise FileNotFoundError(ruta_real) from exc
    return stat.st_mtime_ns, stat.st_size


def cargar_ast_modulo(
    ruta: str,
    *,
    modules_path: str | None = None,
    whitelist: Iterable[str] | None = None,
    expected_fingerprint: FingerprintArchivo | None = None,
):
    """Parsa un módulo Cobra y devuelve su AST."""

    codigo, ruta_real = _leer_codigo_modulo(ruta, modules_path, whitelist)
    if expected_fingerprint is not None:
        if _fingerprint_archivo(ruta_real) != expected_fingerprint:
            raise _ArchivoModuloInestableError(
                f"El módulo cambió durante la lectura: {ruta_real}"
            )
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
def _simbolos_modulo_cache(
    ruta_real: str, fingerprint: FingerprintArchivo
) -> FrozenSet[Tuple[str, str]]:
    """Versión cacheada de :func:`_extraer_simbolos` por ruta+fingerprint."""

    ast_modulo = cargar_ast_modulo(
        ruta_real, expected_fingerprint=fingerprint
    )
    return _extraer_simbolos(ast_modulo)


def obtener_simbolos_modulo(ruta: str) -> set[Tuple[str, str]]:
    """Devuelve los símbolos declarados exportables de un módulo Cobra."""

    _, ruta_real = _normalizar_rutas(ruta)
    for _ in range(2):
        fingerprint = _fingerprint_archivo(ruta_real)
        try:
            return set(_simbolos_modulo_cache(ruta_real, fingerprint))
        except _ArchivoModuloInestableError:
            # El archivo cambió entre la huella previa y la lectura/parsing.
            # Reintentamos con una huella nueva para evitar caché inconsistente.
            continue
    # Si el archivo está cambiando constantemente, hacemos un último intento que
    # puede elevar la excepción natural para que el llamador la gestione.
    fingerprint = _fingerprint_archivo(ruta_real)
    return set(_simbolos_modulo_cache(ruta_real, fingerprint))
