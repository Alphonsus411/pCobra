"""Puente sencillo para cargar bibliotecas C usando ``ctypes``."""

from __future__ import annotations

import ctypes
import os
from typing import Any, Iterable


_cache: dict[str, ctypes.CDLL] = {}

# Lista de prefijos permitidos para cargar bibliotecas
_ALLOWED_PREFIXES: list[str] = [
    os.path.abspath(p)
    for p in os.environ.get(
        "COBRA_ALLOWED_LIB_PATHS", "/usr/lib:/usr/local/lib"
    ).split(os.pathsep)
    if p
]


def _es_ruta_permitida(ruta: str) -> bool:
    path = os.path.abspath(ruta)
    for pref in _ALLOWED_PREFIXES:
        pref = os.path.abspath(pref)
        try:
            if os.path.commonpath([pref, path]) == pref:
                return True
        except ValueError:
            continue
    return False


def cargar_biblioteca(ruta: str) -> ctypes.CDLL:
    """Carga la biblioteca compartida ubicada en ``ruta``.

    La biblioteca se almacena en una caché interna para evitar cargarse
    varias veces. Se devuelve el objeto :class:`ctypes.CDLL` asociado.
    """
    path = os.path.abspath(ruta)
    if not _es_ruta_permitida(path):
        raise ValueError(f"Ruta no permitida: {ruta}")
    if path not in _cache:
        _cache[path] = ctypes.CDLL(path)
    return _cache[path]


def obtener_funcion(lib: ctypes.CDLL, nombre: str,
                    restype: ctypes._CData | None = ctypes.c_int,
                    argtypes: Iterable[ctypes._CData] | None = None) -> Any:
    """Devuelve una función de ``lib`` configurando tipos opcionales."""
    fn = getattr(lib, nombre)
    fn.restype = restype
    if argtypes is not None:
        fn.argtypes = list(argtypes)
    return fn


def cargar_funcion(ruta: str, nombre: str,
                   restype: ctypes._CData | None = ctypes.c_int,
                   argtypes: Iterable[ctypes._CData] | None = None) -> Any:
    """Carga ``ruta`` y devuelve la función indicada."""
    lib = cargar_biblioteca(ruta)
    return obtener_funcion(lib, nombre, restype, argtypes)
